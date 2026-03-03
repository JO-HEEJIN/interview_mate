// swift-tools-version: 5.9
import PackageDescription

let package = Package(
    name: "InterviewMateOverlay",
    platforms: [.macOS(.v13)],
    targets: [
        .executableTarget(
            name: "InterviewMateOverlay",
            path: "Sources/InterviewMateOverlay",
            resources: [
                .copy("../../Resources/Info.plist")
            ]
        )
    ]
)
