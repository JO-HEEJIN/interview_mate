// swift-tools-version: 5.9
import PackageDescription

let package = Package(
    name: "InterviewMateOverlay",
    platforms: [.macOS(.v13)],
    targets: [
        .executableTarget(
            name: "InterviewMateOverlay",
            path: "Sources/InterviewMateOverlay"
            // Info.plist is copied into the .app bundle by build.sh —
            // SPM rejects resource paths outside the target directory.
        )
    ]
)
