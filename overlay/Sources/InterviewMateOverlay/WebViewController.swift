import AppKit
import WebKit

class WebViewController: NSViewController, WKNavigationDelegate, WKUIDelegate, WKScriptMessageHandler {
    private(set) var webView: WKWebView!
    private var currentURL: URL

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

        // Inject JS that patches getDisplayMedia to show a click-to-allow button
        // when WKWebView blocks the call due to missing user gesture
        let patchScript = WKUserScript(
            source: Self.getDisplayMediaPatchJS,
            injectionTime: .atDocumentStart,
            forMainFrameOnly: false
        )
        config.userContentController.addUserScript(patchScript)

        // Capture JS console.log → native NSLog via message handler
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
        config.userContentController.add(self, name: "consoleLog")

        webView = WKWebView(frame: .zero, configuration: config)
        webView.navigationDelegate = self
        webView.uiDelegate = self
        self.view = webView
    }

    override func viewDidLoad() {
        super.viewDidLoad()
        load(url: currentURL)
    }

    func load(url: URL) {
        currentURL = url
        webView.load(URLRequest(url: url))
    }

    // MARK: - Injected JavaScript

    /// When getDisplayMedia fails with "user gesture" error, show a floating button
    /// the user can click — that click IS a native user gesture, so getDisplayMedia succeeds.
    private static let getDisplayMediaPatchJS = """
    (function() {
        console.log('[OverlayPatch] Injecting getDisplayMedia patch');
        if (!navigator.mediaDevices || !navigator.mediaDevices.getDisplayMedia) {
            console.log('[OverlayPatch] No getDisplayMedia support, skipping');
            return;
        }

        const orig = navigator.mediaDevices.getDisplayMedia.bind(navigator.mediaDevices);

        navigator.mediaDevices.getDisplayMedia = function(constraints) {
            console.log('[OverlayPatch] getDisplayMedia called');
            function showPrompt(err) {
                return new Promise(function(resolve, reject) {
                        var overlay = document.createElement('div');
                        overlay.style.cssText = 'position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,0.5);z-index:2147483647;display:flex;align-items:center;justify-content:center;flex-direction:column;gap:12px;';

                        var box = document.createElement('div');
                        box.style.cssText = 'background:white;border-radius:16px;padding:32px;text-align:center;max-width:360px;box-shadow:0 8px 32px rgba(0,0,0,0.3);';

                        var title = document.createElement('div');
                        title.textContent = 'System Audio Capture';
                        title.style.cssText = 'font-size:18px;font-weight:700;margin-bottom:8px;color:#1a1a1a;';

                        var desc = document.createElement('div');
                        desc.textContent = 'Click the button below to share your screen audio.';
                        desc.style.cssText = 'font-size:14px;color:#666;margin-bottom:20px;';

                        var btn = document.createElement('button');
                        btn.textContent = 'Enable Screen Sharing';
                        btn.style.cssText = 'padding:12px 28px;font-size:16px;font-weight:600;border-radius:10px;border:none;background:#4F46E5;color:white;cursor:pointer;transition:background 0.2s;';
                        btn.onmouseenter = function() { btn.style.background = '#4338CA'; };
                        btn.onmouseleave = function() { btn.style.background = '#4F46E5'; };

                        btn.onclick = function() {
                            overlay.remove();
                            orig(constraints).then(resolve).catch(reject);
                        };

                        var cancel = document.createElement('button');
                        cancel.textContent = 'Cancel';
                        cancel.style.cssText = 'padding:8px 20px;font-size:14px;border-radius:8px;border:1px solid #ddd;background:white;color:#666;cursor:pointer;margin-top:8px;';
                        cancel.onclick = function() {
                            overlay.remove();
                            reject(new DOMException('User cancelled', 'NotAllowedError'));
                        };

                        box.appendChild(title);
                        box.appendChild(desc);
                        box.appendChild(btn);
                        box.appendChild(cancel);
                        overlay.appendChild(box);
                        document.body.appendChild(overlay);
                    });
            }

            try {
                var result = orig(constraints);
                console.log('[OverlayPatch] orig() returned promise');
                return result.catch(function(err) {
                    console.log('[OverlayPatch] Promise rejected:', err.name, err.message);
                    if (err.message && err.message.includes('user gesture')) {
                        return showPrompt(err);
                    }
                    throw err;
                });
            } catch(err) {
                console.log('[OverlayPatch] Sync throw caught:', err.name, err.message);
                if (err.message && err.message.includes('user gesture')) {
                    return showPrompt(err);
                }
                throw err;
            }
        };
    })();
    """

    // MARK: - WKScriptMessageHandler

    func userContentController(_ userContentController: WKUserContentController, didReceive message: WKScriptMessage) {
        if message.name == "consoleLog", let body = message.body as? String {
            NSLog("[JS] %@", body)
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
