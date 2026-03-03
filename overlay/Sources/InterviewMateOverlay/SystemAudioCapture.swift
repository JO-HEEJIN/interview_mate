import AVFoundation
import ScreenCaptureKit

/// Captures system audio via ScreenCaptureKit and delivers Float32 PCM data.
class SystemAudioCapture: NSObject, SCStreamDelegate, SCStreamOutput {
    private var stream: SCStream?
    private var isCapturing = false
    private var bufferCount = 0

    /// Called with base64-encoded Float32 PCM audio data
    var onAudioData: ((String) -> Void)?
    var onError: ((String) -> Void)?
    var onStopped: (() -> Void)?

    func startCapture() async {
        guard !isCapturing else { return }

        do {
            let content = try await SCShareableContent.excludingDesktopWindows(false, onScreenWindowsOnly: true)

            guard let display = content.displays.first else {
                onError?("No display found for audio capture.")
                return
            }

            let config = SCStreamConfiguration()
            config.capturesAudio = true
            config.excludesCurrentProcessAudio = true
            config.channelCount = 1
            config.sampleRate = 16000

            let filter = SCContentFilter(display: display, excludingWindows: [])

            stream = SCStream(filter: filter, configuration: config, delegate: self)
            try stream?.addStreamOutput(self, type: .audio, sampleHandlerQueue: .global(qos: .userInteractive))
            try await stream?.startCapture()

            isCapturing = true
            bufferCount = 0
            NSLog("SystemAudioCapture: started (display: %dx%d)", Int(display.width), Int(display.height))
        } catch {
            onError?("Failed to start audio capture: \(error.localizedDescription)")
        }
    }

    func stopCapture() {
        guard isCapturing else { return }
        isCapturing = false
        NSLog("SystemAudioCapture: stopping after %d buffers", bufferCount)

        Task {
            try? await stream?.stopCapture()
            stream = nil
            NSLog("SystemAudioCapture: stopped")
        }
    }

    // MARK: - SCStreamOutput

    func stream(_ stream: SCStream, didOutputSampleBuffer sampleBuffer: CMSampleBuffer, of type: SCStreamOutputType) {
        guard type == .audio, isCapturing else { return }

        guard let blockBuffer = sampleBuffer.dataBuffer else { return }

        var length = 0
        var dataPointer: UnsafeMutablePointer<Int8>?
        let status = CMBlockBufferGetDataPointer(blockBuffer, atOffset: 0, lengthAtOffsetOut: nil, totalLengthOut: &length, dataPointerOut: &dataPointer)

        guard status == kCMBlockBufferNoErr, let dataPointer, length > 0 else { return }

        bufferCount += 1

        // Log every 100th buffer to track data flow without flooding
        if bufferCount % 100 == 1 {
            // Check if audio has non-zero samples (not silence)
            let floatCount = length / 4
            let floatPointer = UnsafeRawPointer(dataPointer).bindMemory(to: Float32.self, capacity: floatCount)
            var maxAmplitude: Float32 = 0
            for i in 0..<floatCount {
                let abs = Swift.abs(floatPointer[i])
                if abs > maxAmplitude { maxAmplitude = abs }
            }
            NSLog("SystemAudioCapture: buffer #%d, %d bytes (%d samples), maxAmp=%.6f", bufferCount, length, floatCount, maxAmplitude)
        }

        let data = Data(bytes: dataPointer, count: length)
        let base64 = data.base64EncodedString()

        DispatchQueue.main.async { [weak self] in
            self?.onAudioData?(base64)
        }
    }

    // MARK: - SCStreamDelegate

    func stream(_ stream: SCStream, didStopWithError error: Error) {
        NSLog("SystemAudioCapture: stream stopped with error: \(error.localizedDescription)")
        isCapturing = false
        DispatchQueue.main.async { [weak self] in
            self?.onStopped?()
        }
    }
}
