// public/audio-processor.js
class AudioProcessor extends AudioWorkletProcessor {
  process(inputs, outputs, parameters) {
    const input = inputs[0];
    const inputChannel = input[0];

    if (inputChannel) {
      // Calculate RMS level
      let sum = 0;
      for (let i = 0; i < inputChannel.length; i++) {
        sum += inputChannel[i] * inputChannel[i];
      }
      const rms = Math.sqrt(sum / inputChannel.length);
      const level = Math.min(100, rms * 200);

      // Send level to main thread
      this.port.postMessage({ type: 'audio-level', level });
    }

    return true;
  }
}

registerProcessor('audio-processor', AudioProcessor);