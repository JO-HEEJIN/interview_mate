import AppKit
import WebKit

class WebViewController: NSViewController, WKNavigationDelegate, WKUIDelegate, WKScriptMessageHandler {
    private(set) var webView: WKWebView!
    private var currentURL: URL
    private let audioCapture = SystemAudioCapture()

    /// Called by AppDelegate on app termination to clean up ScreenCaptureKit resources
    func stopAudioCapture() {
        audioCapture.stopCapture()
    }

    init(url: URL) {
        self.currentURL = url
        super.init(nibName: nil, bundle: nil)
    }

    @available(*, unavailable)
    required init?(coder: NSCoder) {
        fatalError("init(coder:) has not been implemented")
    }

    override func loadView() {
        let config = WKWebViewConfiguration()
        config.mediaTypesRequiringUserActionForPlayback = []
        config.preferences.setValue(true, forKey: "developerExtrasEnabled")
        config.preferences.setValue(true, forKey: "mediaDevicesEnabled")
        config.preferences.setValue(true, forKey: "screenCaptureEnabled")

        // JS → Native message handlers
        config.userContentController.add(self, name: "startSystemAudio")
        config.userContentController.add(self, name: "stopSystemAudio")
        config.userContentController.add(self, name: "consoleLog")

        // Console.log bridge — injected FIRST so patch logs are visible
        let consoleScript = WKUserScript(
            source: """
            (function() {
                var origLog = console.log;
                console.log = function() {
                    var msg = Array.prototype.slice.call(arguments).join(' ');
                    origLog.apply(console, arguments);
                    try { window.webkit.messageHandlers.consoleLog.postMessage(msg); } catch(e) {}
                };
            })();
            """,
            injectionTime: .atDocumentStart,
            forMainFrameOnly: false
        )
        config.userContentController.addUserScript(consoleScript)

        // Inject: override getDisplayMedia to use native ScreenCaptureKit audio
        let patchScript = WKUserScript(
            source: Self.nativeAudioBridgeJS,
            injectionTime: .atDocumentStart,
            forMainFrameOnly: false
        )
        config.userContentController.addUserScript(patchScript)

        webView = WKWebView(frame: .zero, configuration: config)
        webView.navigationDelegate = self
        webView.uiDelegate = self
        self.view = webView

        setupAudioCapture()
    }

    override func viewDidLoad() {
        super.viewDidLoad()
        load(url: currentURL)
    }

    func load(url: URL) {
        currentURL = url
        webView.load(URLRequest(url: url))
    }

    // MARK: - Native Audio Capture Bridge

    private var nativeSendCount = 0

    private func setupAudioCapture() {
        audioCapture.onAudioData = { [weak self] base64 in
            guard let self else { return }
            self.nativeSendCount += 1
            if self.nativeSendCount % 100 == 1 {
                NSLog("Native→JS: sending audio chunk #%d (%d chars)", self.nativeSendCount, base64.count)
            }
            self.webView.evaluateJavaScript("window.__nativeAudioReceive('\(base64)')") { _, error in
                if let error {
                    NSLog("Native→JS evaluateJavaScript error: %@", error.localizedDescription)
                }
            }
        }

        audioCapture.onError = { [weak self] error in
            self?.webView.evaluateJavaScript("window.__nativeAudioError('\(error)')", completionHandler: nil)
        }

        audioCapture.onStopped = { [weak self] in
            self?.webView.evaluateJavaScript("window.__nativeAudioStopped()", completionHandler: nil)
        }
    }

    // MARK: - Injected JavaScript

    /// Overrides getDisplayMedia to use native ScreenCaptureKit for system audio.
    /// Flow:
    /// 1. Web app calls getDisplayMedia({audio:true, video:true})
    /// 2. JS sends "startSystemAudio" message to native
    /// 3. Native captures system audio via ScreenCaptureKit
    /// 4. Native sends Float32 PCM data (base64) back to JS
    /// 5. JS decodes → feeds into ScriptProcessorNode → MediaStreamDestination
    /// 6. getDisplayMedia resolves with the MediaStream (has audio track)
    private static let nativeAudioBridgeJS = """
    (function() {
        // Shared audio queue — frontend reads directly from this
        var audioQueue = [];
        var isCapturing = false;
        var jsReceiveCount = 0;

        // Expose queue globally so frontend AudioContext can read it directly
        window.__nativeAudioQueue = audioQueue;
        window.__nativeAudioCapturing = false;

        // Called by native when audio data arrives
        window.__nativeAudioReceive = function(base64) {
            if (!isCapturing) return;
            jsReceiveCount++;
            if (jsReceiveCount % 100 === 1) {
                console.log('[NativeAudio] JS received chunk #' + jsReceiveCount + ', queueLen=' + audioQueue.length);
            }
            try {
                var raw = atob(base64);
                var ab = new ArrayBuffer(raw.length);
                var view = new Uint8Array(ab);
                for (var i = 0; i < raw.length; i++) {
                    view[i] = raw.charCodeAt(i);
                }
                audioQueue.push(new Float32Array(ab));
                // Prevent unbounded queue growth (keep ~2 seconds at 50 chunks/sec)
                while (audioQueue.length > 100) { audioQueue.shift(); }
            } catch(e) {
                console.log('[NativeAudio] Error decoding audio:', e.message);
            }
        };

        window.__nativeAudioError = function(msg) {
            console.log('[NativeAudio] Error:', msg);
        };

        window.__nativeAudioStopped = function() {
            console.log('[NativeAudio] Capture stopped');
            isCapturing = false;
            window.__nativeAudioCapturing = false;
            audioQueue.length = 0;
        };

        // The patched getDisplayMedia — returns a dummy stream with an audio track.
        // The REAL audio mixing happens in the frontend via __nativeAudioQueue.
        function patchedGetDisplayMedia(constraints) {
            console.log('[NativeAudio] getDisplayMedia INTERCEPTED — using native ScreenCaptureKit');
            return new Promise(function(resolve, reject) {
                try {
                    isCapturing = true;
                    window.__nativeAudioCapturing = true;
                    audioQueue.length = 0;
                    jsReceiveCount = 0;

                    // Tell native to start capturing system audio
                    window.webkit.messageHandlers.startSystemAudio.postMessage({});

                    // Create a dummy audio stream using an AudioContext
                    // This lets the frontend know "display capture is active" and triggers mixing
                    var dummyCtx = new (window.AudioContext || window.webkitAudioContext)({ sampleRate: 16000 });
                    var oscillator = dummyCtx.createOscillator();
                    oscillator.frequency.value = 0; // Silent
                    var dest = dummyCtx.createMediaStreamDestination();
                    oscillator.connect(dest);
                    oscillator.start();

                    setTimeout(function() {
                        var stream = dest.stream;
                        if (stream && stream.getAudioTracks().length > 0) {
                            // Add dummy video track
                            var canvas = document.createElement('canvas');
                            canvas.width = 1;
                            canvas.height = 1;
                            var videoStream = canvas.captureStream(0);
                            var videoTrack = videoStream.getVideoTracks()[0];

                            var combinedStream = new MediaStream();
                            stream.getAudioTracks().forEach(function(t) {
                                combinedStream.addTrack(t);
                                // Auto-stop native capture when track ends (recording stops)
                                t.onended = function() {
                                    console.log('[NativeAudio] Dummy track ended — stopping native capture');
                                    isCapturing = false;
                                    window.__nativeAudioCapturing = false;
                                    audioQueue.length = 0;
                                    try { window.webkit.messageHandlers.stopSystemAudio.postMessage({}); } catch(e) {}
                                };
                            });
                            if (videoTrack) combinedStream.addTrack(videoTrack);

                            console.log('[NativeAudio] Returning dummy stream. Real audio via __nativeAudioQueue');
                            resolve(combinedStream);
                        } else {
                            reject(new Error('Failed to create dummy audio stream'));
                        }
                    }, 300);
                } catch(e) {
                    console.log('[NativeAudio] Setup error:', e.message);
                    reject(e);
                }
            });
        }

        // Replace navigator.mediaDevices with Proxy to permanently intercept getDisplayMedia
        if (navigator.mediaDevices) {
            var realMediaDevices = navigator.mediaDevices;

            var proxyHandler = {
                get: function(target, prop, receiver) {
                    if (prop === 'getDisplayMedia') {
                        return patchedGetDisplayMedia;
                    }
                    var val = target[prop];
                    if (typeof val === 'function') {
                        return val.bind(target);
                    }
                    return val;
                },
                set: function(target, prop, value) {
                    target[prop] = value;
                    return true;
                }
            };

            var proxy = new Proxy(realMediaDevices, proxyHandler);

            try {
                Object.defineProperty(navigator, 'mediaDevices', {
                    get: function() { return proxy; },
                    configurable: true
                });
                console.log('[NativeAudio] Proxy active. Audio queue exposed at window.__nativeAudioQueue');
            } catch(e) {
                console.log('[NativeAudio] Proxy failed:', e.message);
                navigator.mediaDevices.getDisplayMedia = patchedGetDisplayMedia;
            }
        }
    })();
    """

    // MARK: - WKScriptMessageHandler

    func userContentController(_ userContentController: WKUserContentController, didReceive message: WKScriptMessage) {
        switch message.name {
        case "startSystemAudio":
            NSLog("Starting native system audio capture")
            Task { await audioCapture.startCapture() }
        case "stopSystemAudio":
            NSLog("Stopping native system audio capture")
            audioCapture.stopCapture()
        case "consoleLog":
            if let body = message.body as? String {
                NSLog("[JS] %@", body)
            }
        default:
            break
        }
    }

    // MARK: - WKUIDelegate

    func webView(
        _ webView: WKWebView,
        requestMediaCapturePermissionFor origin: WKSecurityOrigin,
        initiatedByFrame frame: WKFrameInfo,
        type: WKMediaCaptureType,
        decisionHandler: @escaping (WKPermissionDecision) -> Void
    ) {
        decisionHandler(.grant)
    }

    func webView(_ webView: WKWebView, didFail navigation: WKNavigation!, withError error: Error) {
        NSLog("WebView navigation failed: \(error.localizedDescription)")
    }

    func webView(_ webView: WKWebView, didFailProvisionalNavigation navigation: WKNavigation!, withError error: Error) {
        NSLog("WebView provisional navigation failed: \(error.localizedDescription)")
    }

    func webView(_ webView: WKWebView, didFinish navigation: WKNavigation!) {
        NSLog("WebView loaded: \(webView.url?.absoluteString ?? "unknown")")

        // Re-apply the getDisplayMedia patch after page load to ensure it sticks
        webView.evaluateJavaScript(Self.nativeAudioBridgeJS) { _, error in
            if let error {
                NSLog("Patch injection error: \(error.localizedDescription)")
            } else {
                NSLog("Native audio patch applied successfully after page load")
            }
        }
    }

    func webView(
        _ webView: WKWebView,
        createWebViewWith configuration: WKWebViewConfiguration,
        for navigationAction: WKNavigationAction,
        windowFeatures: WKWindowFeatures
    ) -> WKWebView? {
        if navigationAction.targetFrame == nil || navigationAction.targetFrame?.isMainFrame == false {
            webView.load(navigationAction.request)
        }
        return nil
    }
}
