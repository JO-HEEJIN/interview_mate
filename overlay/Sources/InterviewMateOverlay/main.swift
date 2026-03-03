import AppKit

// Always log to file so Finder-launched instances can be debugged
let logPath = (NSHomeDirectory() as NSString).appendingPathComponent("Library/Logs/InterviewMateOverlay.log")
// Truncate if larger than 5MB
if let attrs = try? FileManager.default.attributesOfItem(atPath: logPath),
   let size = attrs[.size] as? Int, size > 5_000_000 {
    FileManager.default.createFile(atPath: logPath, contents: nil)
}
freopen(logPath, "a", stderr)

NSLog("=== InterviewMateOverlay started (PID %d) ===", ProcessInfo.processInfo.processIdentifier)
NSLog("Log file: %@", logPath)

let app = NSApplication.shared
let delegate = AppDelegate()
app.delegate = delegate
app.run()
