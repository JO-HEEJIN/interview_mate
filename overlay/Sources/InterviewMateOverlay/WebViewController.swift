import AppKit
import WebKit

class WebViewController: NSViewController, WKNavigationDelegate, WKUIDelegate {
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

        webView = WKWebView(frame: .zero, configuration: config)
        webView.navigationDelegate = self
        webView.uiDelegate = self
        webView.setValue(false, forKey: "drawsBackground")

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

    // MARK: - WKUIDelegate

    // Handle permission requests (microphone for speech recognition)
    func webView(
        _ webView: WKWebView,
        requestMediaCapturePermissionFor origin: WKSecurityOrigin,
        initiatedByFrame frame: WKFrameInfo,
        type: WKMediaCaptureType,
        decisionHandler: @escaping (WKPermissionDecision) -> Void
    ) {
        decisionHandler(.grant)
    }

    // Handle window.open / target="_blank" links
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
