import AppKit

class OverlayWindow: NSWindow {
    override var canBecomeKey: Bool { true }
    override var canBecomeMain: Bool { true }

    convenience init(contentRect: NSRect) {
        self.init(
            contentRect: contentRect,
            styleMask: [.titled, .closable, .resizable, .miniaturizable],
            backing: .buffered,
            defer: false
        )

        title = "InterviewMate Overlay"
        level = .floating
        isOpaque = false
        alphaValue = 0.85
        backgroundColor = .clear
        hasShadow = false
        isReleasedWhenClosed = false
        minSize = NSSize(width: 320, height: 400)

        // Restore last window position or center
        if !setFrameUsingName("OverlayWindow") {
            center()
        }
        setFrameAutosaveName("OverlayWindow")
    }
}
