import AppKit

protocol OverlayWindowDelegate: AnyObject {
    func overlayWindowAdjustOpacity(by delta: Double)
    func overlayWindowToggleClickThrough()
    func overlayWindowToggleAlwaysOnTop()
}

class OverlayWindow: NSWindow {
    override var canBecomeKey: Bool { true }
    override var canBecomeMain: Bool { true }

    weak var shortcutDelegate: OverlayWindowDelegate?

    convenience init(contentRect: NSRect) {
        self.init(
            contentRect: contentRect,
            styleMask: [.titled, .closable, .resizable, .miniaturizable],
            backing: .buffered,
            defer: false
        )

        title = "InterviewMate Overlay"
        level = .floating
        alphaValue = 0.85
        hasShadow = false
        isReleasedWhenClosed = false
        minSize = NSSize(width: 320, height: 400)

        // Restore last window position or center
        if !setFrameUsingName("OverlayWindow") {
            center()
        }
        setFrameAutosaveName("OverlayWindow")
    }

    // Intercept key events before WKWebView consumes them
    override func performKeyEquivalent(with event: NSEvent) -> Bool {
        let flags = event.modifierFlags.intersection(.deviceIndependentFlagsMask)

        // ⌘↑ Increase opacity
        if flags == .command && event.keyCode == 126 {
            shortcutDelegate?.overlayWindowAdjustOpacity(by: 0.1)
            return true
        }
        // ⌘↓ Decrease opacity
        if flags == .command && event.keyCode == 125 {
            shortcutDelegate?.overlayWindowAdjustOpacity(by: -0.1)
            return true
        }
        // ⌘⇧T is handled by Carbon global hotkey (AppDelegate) — not here, to avoid double-toggle
        // ⌘⇧P Always-on-top toggle
        if flags == [.command, .shift] && event.charactersIgnoringModifiers?.lowercased() == "p" {
            shortcutDelegate?.overlayWindowToggleAlwaysOnTop()
            return true
        }

        return super.performKeyEquivalent(with: event)
    }
}
