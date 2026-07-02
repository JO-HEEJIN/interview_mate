import AVFoundation
import ScreenCaptureKit

/// Captures system audio via ScreenCaptureKit and delivers Float32 PCM data.
///
/// Threading model: all mutable state is owned by `queue` (a serial queue).
/// SCStream callbacks are delivered on `queue`; start/stop hop onto it.
class SystemAudioCapture: NSObject, SCStreamDelegate, SCStreamOutput {
    private var stream: SCStream?
    private var isCapturing = false
    private var isStarting = false
    private var bufferCount = 0
    private var silentBufferCount = 0
    private var lastBufferAt = Date.distantPast
    private var watchdog: DispatchSourceTimer?

    // ~50 buffers/sec. Silence alone is NORMAL during an interview (remote side
    // listening, participant muted), so it must not trigger a restart on its own
    // for a long time. A dead stream is different: buffers stop arriving entirely.
    private let silentThreshold = 6000            // ~120s of continuous digital silence
    private let bufferTimeout: TimeInterval = 10  // no buffers at all for 10s = dead stream

    /// Serial queue that owns all mutable state and receives stream callbacks.
    private let queue = DispatchQueue(label: "ing.interviewmate.audiocapture", qos: .userInteractive)

    /// Called with base64-encoded Float32 PCM audio data (on main thread)
    var onAudioData: ((String) -> Void)?
    var onError: ((String) -> Void)?
    var onStopped: (() -> Void)?

    func startCapture() async {
        // Reject overlapping starts (e.g. JS sends startSystemAudio twice)
        let alreadyStarting: Bool = queue.sync {
            if isStarting { return true }
            isStarting = true
            return false
        }
        if alreadyStarting {
            NSLog("SystemAudioCapture: start already in progress — ignoring")
            return
        }
        defer { queue.sync { isStarting = false } }

        // Always tear down any existing stream first to prevent resource conflicts
        await teardownStream()

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

            let newStream = SCStream(filter: filter, configuration: config, delegate: self)
            try newStream.addStreamOutput(self, type: .audio, sampleHandlerQueue: queue)
            try await newStream.startCapture()

            queue.sync {
                stream = newStream
                isCapturing = true
                bufferCount = 0
                silentBufferCount = 0
                lastBufferAt = Date()
                startWatchdog_onQueue()
            }
            NSLog("SystemAudioCapture: started (display: %dx%d)", Int(display.width), Int(display.height))
        } catch {
            NSLog("SystemAudioCapture: startCapture FAILED: %@", error.localizedDescription)
            onError?("Failed to start audio capture: \(error.localizedDescription)")
        }
    }

    func stopCapture() {
        Task { await teardownStream() }
    }

    private func teardownStream() async {
        let old: SCStream? = queue.sync {
            guard stream != nil || isCapturing else { return nil }
            isCapturing = false
            watchdog?.cancel()
            watchdog = nil
            NSLog("SystemAudioCapture: stopping after %d buffers", bufferCount)
            let s = stream
            stream = nil
            return s
        }
        if let old {
            try? await old.stopCapture()
            NSLog("SystemAudioCapture: stopped")
        }
    }

    // MARK: - Watchdog (all methods below run on `queue`)

    private func startWatchdog_onQueue() {
        watchdog?.cancel()
        let timer = DispatchSource.makeTimerSource(queue: queue)
        timer.schedule(deadline: .now() + 5, repeating: 5)
        timer.setEventHandler { [weak self] in self?.watchdogTick_onQueue() }
        timer.resume()
        watchdog = timer
    }

    private func watchdogTick_onQueue() {
        guard isCapturing else { return }

        let sinceLastBuffer = Date().timeIntervalSince(lastBufferAt)
        let deadStream = sinceLastBuffer > bufferTimeout
        let staleStream = silentBufferCount >= silentThreshold
        guard deadStream || staleStream else { return }

        NSLog("SystemAudioCapture: watchdog restart (noBuffersFor=%.1fs, silentBuffers=%d)",
              sinceLastBuffer, silentBufferCount)
        silentBufferCount = 0
        lastBufferAt = Date()  // avoid immediate re-trigger while restart is in flight
        Task { [weak self] in
            await self?.startCapture()
        }
    }

    // MARK: - SCStreamOutput (delivered on `queue`)

    func stream(_ stream: SCStream, didOutputSampleBuffer sampleBuffer: CMSampleBuffer, of type: SCStreamOutputType) {
        guard type == .audio, isCapturing else { return }

        guard let blockBuffer = sampleBuffer.dataBuffer else { return }

        var length = 0
        var dataPointer: UnsafeMutablePointer<Int8>?
        let status = CMBlockBufferGetDataPointer(blockBuffer, atOffset: 0, lengthAtOffsetOut: nil, totalLengthOut: &length, dataPointerOut: &dataPointer)

        guard status == kCMBlockBufferNoErr, let dataPointer, length > 0 else { return }

        bufferCount += 1
        lastBufferAt = Date()

        // Check amplitude for silence tracking
        let floatCount = length / 4
        let floatPointer = UnsafeRawPointer(dataPointer).bindMemory(to: Float32.self, capacity: floatCount)
        var maxAmplitude: Float32 = 0
        for i in 0..<floatCount {
            let abs = Swift.abs(floatPointer[i])
            if abs > maxAmplitude { maxAmplitude = abs }
        }

        if maxAmplitude < 0.0001 {
            silentBufferCount += 1
        } else {
            silentBufferCount = 0
        }

        // Log every 100th buffer
        if bufferCount % 100 == 1 {
            NSLog("SystemAudioCapture: buffer #%d, %d bytes (%d samples), maxAmp=%.6f, silent=%d/%d",
                  bufferCount, length, floatCount, maxAmplitude, silentBufferCount, silentThreshold)
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
        queue.async { [weak self] in
            guard let self else { return }
            self.isCapturing = false
            self.watchdog?.cancel()
            self.watchdog = nil
            self.stream = nil
        }
        DispatchQueue.main.async { [weak self] in
            self?.onStopped?()
        }
    }
}
