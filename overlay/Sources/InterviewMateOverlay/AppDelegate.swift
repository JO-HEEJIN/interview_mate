import AppKit
import WebKit

class AppDelegate: NSObject, NSApplicationDelegate {
    private var window: OverlayWindow!
    private var webViewController: WebViewController!
    private var statusItem: NSStatusItem!
    private var opacitySlider: NSSlider!
    private var alwaysOnTopItem: NSMenuItem!
    private var clickThroughItem: NSMenuItem!
    private var defaultURL = URL(string: "https://interviewmate.ing")!

    // MARK: - App Lifecycle

    func applicationDidFinishLaunching(_ notification: Notification) {
        setupWindow()
        setupMenuBar()
        setupKeyboardShortcuts()
        window.makeKeyAndOrderFront(nil)
        NSApp.activate(ignoringOtherApps: true)
    }

    func applicationShouldHandleReopen(_ sender: NSApplication, hasVisibleWindows flag: Bool) -> Bool {
        if !flag {
            window.makeKeyAndOrderFront(nil)
        }
        return true
    }

    // MARK: - Window Setup

    private func setupWindow() {
        let screenFrame = NSScreen.main?.visibleFrame ?? NSRect(x: 0, y: 0, width: 800, height: 600)
        let windowWidth: CGFloat = 480
        let windowHeight: CGFloat = 680
        let contentRect = NSRect(
            x: screenFrame.maxX - windowWidth - 20,
            y: screenFrame.midY - windowHeight / 2,
            width: windowWidth,
            height: windowHeight
        )

        window = OverlayWindow(contentRect: contentRect)
        webViewController = WebViewController(url: defaultURL)
        window.contentViewController = webViewController
    }

    // MARK: - Menu Bar

    private func setupMenuBar() {
        statusItem = NSStatusBar.system.statusItem(withLength: NSStatusItem.variableLength)

        if let button = statusItem.button {
            button.image = NSImage(
                systemSymbolName: "rectangle.on.rectangle",
                accessibilityDescription: "InterviewMate Overlay"
            )
        }

        let menu = NSMenu()

        // Show/Hide window
        let showItem = NSMenuItem(title: "Show Window", action: #selector(showWindow), keyEquivalent: "")
        showItem.target = self
        menu.addItem(showItem)

        menu.addItem(.separator())

        // Opacity label
        let opacityLabel = NSMenuItem(title: "Opacity", action: nil, keyEquivalent: "")
        opacityLabel.isEnabled = false
        menu.addItem(opacityLabel)

        // Opacity slider
        opacitySlider = NSSlider(value: 0.85, minValue: 0.1, maxValue: 1.0, target: self, action: #selector(opacityChanged))
        opacitySlider.frame = NSRect(x: 18, y: 0, width: 180, height: 24)
        opacitySlider.isContinuous = true

        let sliderView = NSView(frame: NSRect(x: 0, y: 0, width: 216, height: 30))
        sliderView.addSubview(opacitySlider)

        let sliderItem = NSMenuItem()
        sliderItem.view = sliderView
        menu.addItem(sliderItem)

        menu.addItem(.separator())

        // Always on top toggle
        alwaysOnTopItem = NSMenuItem(title: "Always on Top", action: #selector(toggleAlwaysOnTop), keyEquivalent: "")
        alwaysOnTopItem.target = self
        alwaysOnTopItem.state = .on
        menu.addItem(alwaysOnTopItem)

        // Click-through toggle
        clickThroughItem = NSMenuItem(title: "Click Through", action: #selector(toggleClickThrough), keyEquivalent: "")
        clickThroughItem.target = self
        clickThroughItem.state = .off
        menu.addItem(clickThroughItem)

        menu.addItem(.separator())

        // Change URL
        let urlItem = NSMenuItem(title: "Change URL…", action: #selector(changeURL), keyEquivalent: "")
        urlItem.target = self
        menu.addItem(urlItem)

        // Reload
        let reloadItem = NSMenuItem(title: "Reload", action: #selector(reloadPage), keyEquivalent: "r")
        reloadItem.target = self
        reloadItem.keyEquivalentModifierMask = [.command]
        menu.addItem(reloadItem)

        menu.addItem(.separator())

        // Quit
        let quitItem = NSMenuItem(title: "Quit", action: #selector(NSApplication.terminate(_:)), keyEquivalent: "q")
        menu.addItem(quitItem)

        statusItem.menu = menu
    }

    // MARK: - Keyboard Shortcuts

    private func setupKeyboardShortcuts() {
        // ⌘↑ Increase opacity
        NSEvent.addLocalMonitorForEvents(matching: .keyDown) { [weak self] event in
            guard let self else { return event }
            let flags = event.modifierFlags.intersection(.deviceIndependentFlagsMask)

            // ⌘↑ Increase opacity
            if flags == .command && event.keyCode == 126 {
                self.adjustOpacity(by: 0.1)
                return nil
            }
            // ⌘↓ Decrease opacity
            if flags == .command && event.keyCode == 125 {
                self.adjustOpacity(by: -0.1)
                return nil
            }
            // ⌘⇧T Click-through toggle
            if flags == [.command, .shift] && event.charactersIgnoringModifiers?.lowercased() == "t" {
                self.toggleClickThrough()
                return nil
            }
            // ⌘⇧P Always-on-top toggle
            if flags == [.command, .shift] && event.charactersIgnoringModifiers?.lowercased() == "p" {
                self.toggleAlwaysOnTop()
                return nil
            }

            return event
        }
    }

    // MARK: - Actions

    @objc private func showWindow() {
        window.makeKeyAndOrderFront(nil)
        NSApp.activate(ignoringOtherApps: true)
    }

    @objc private func opacityChanged() {
        window.alphaValue = CGFloat(opacitySlider.doubleValue)
    }

    private func adjustOpacity(by delta: Double) {
        let newValue = max(0.1, min(1.0, Double(window.alphaValue) + delta))
        window.alphaValue = CGFloat(newValue)
        opacitySlider.doubleValue = newValue
    }

    @objc private func toggleAlwaysOnTop() {
        if window.level == .floating {
            window.level = .normal
            alwaysOnTopItem.state = .off
        } else {
            window.level = .floating
            alwaysOnTopItem.state = .on
        }
    }

    @objc private func toggleClickThrough() {
        let newValue = !window.ignoresMouseEvents
        window.ignoresMouseEvents = newValue
        clickThroughItem.state = newValue ? .on : .off

        // Visual feedback: dim slightly when click-through is on
        if newValue {
            window.alphaValue = min(CGFloat(opacitySlider.doubleValue), 0.5)
        } else {
            window.alphaValue = CGFloat(opacitySlider.doubleValue)
        }
    }

    @objc private func changeURL() {
        let alert = NSAlert()
        alert.messageText = "Enter URL"
        alert.informativeText = "Enter the InterviewMate URL to load:"
        alert.addButton(withTitle: "Load")
        alert.addButton(withTitle: "Cancel")

        let input = NSTextField(frame: NSRect(x: 0, y: 0, width: 300, height: 24))
        input.stringValue = defaultURL.absoluteString
        alert.accessoryView = input

        let response = alert.runModal()
        if response == .alertFirstButtonReturn {
            let urlString = input.stringValue.trimmingCharacters(in: .whitespacesAndNewlines)
            if let url = URL(string: urlString) {
                defaultURL = url
                webViewController.load(url: url)
            }
        }
    }

    @objc private func reloadPage() {
        webViewController.webView.reload()
    }
}
