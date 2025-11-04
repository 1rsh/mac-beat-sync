import sounddevice as sd
import time
from .utils.audio import AudioProcessor
from .utils.keyboard import MacKeyboardController

def main(device_index: int | None = None):
    devices = sd.query_devices()

    # Choose BlackHole if available
    blackhole_index = None
    for i, d in enumerate(devices):
        if "blackhole" in d['name'].lower():
            blackhole_index = i

    if device_index is None:
        if blackhole_index is not None:
            device_index = blackhole_index
        else:
            device_index = int(input("\nEnter input device index (e.g., 0): "))

    device_info = sd.query_devices(device_index)
    channels = min(device_info['max_input_channels'], 2)

    audio = AudioProcessor()
    keyboard = MacKeyboardController()

    def callback(indata, frames, time_info, status):
        if status:
            print(status)
        current_time = time.time()
        if current_time - audio.last_update_time < audio.config.audio.UPDATE_INTERVAL:
            return
        audio.last_update_time = current_time

        raw, processed = audio.process_audio(indata)
        keyboard.set_brightness(processed)
        keyboard.update_raw(raw)

    try:
        with sd.InputStream(
            device=device_index,
            channels=channels,
            samplerate=audio.config.audio.SAMPLE_RATE,
            blocksize=audio.config.audio.BLOCK_SIZE,
            callback=callback,
        ):
            while True:
                time.sleep(0.05)
    except KeyboardInterrupt:
        keyboard.set_brightness(0.2)
        keyboard.close()
        print("\n💡 Keyboard set to default. Exiting.")


if __name__ == "__main__":
    main()