import numpy as np
from collections import deque

from .utils import get_config

class AudioProcessor:
    """
    Processes incoming audio blocks and computes a normalized brightness/intensity value (0–1).

    Combines:
      - RMS loudness (energy)
      - Spectral flux (onset/beat detection)
      - Spectral centroid (timbre brightness)
    Smooths transitions and applies gamma correction for perceptual brightness control.
    """

    def __init__(self):
        self.config = get_config()

        # Audio parameters
        self.smoothing = self.config.audio.SMOOTHING
        self.block_size = self.config.audio.BLOCK_SIZE
        self.sample_rate = self.config.audio.SAMPLE_RATE

        # Rolling windows
        self.window = deque(
            maxlen=int(
                self.config.audio.WINDOW_SECONDS
                * self.sample_rate
                / self.block_size
            )
        )
        self.smoothed_level = 0.0
        self.last_update_time = 0.0

        # Previous magnitude spectrum for flux calculation
        self.prev_mag = np.zeros(self.block_size // 2 + 1)
        self.recent_flux = deque(maxlen=10)

        # Dynamic normalization buffers
        self.rms_history = deque(maxlen=100)
        self.flux_history = deque(maxlen=100)

    def process_audio(self, indata) -> tuple[float, float]:
        """
        Processes a block of audio data and returns two brightness values (raw, smoothed),
        both in range [0, 1].

        Args:
            indata (np.ndarray): audio frame, shape (block_size, channels)

        Returns:
            tuple(float, float): (raw_brightness, smoothed_brightness)
        """
        # Convert to mono
        mono = np.mean(indata, axis=1)

        # --- RMS Energy ---
        rms = np.sqrt(np.mean(np.square(mono)))
        self.window.append(rms)
        self.rms_history.append(rms)

        # Early exit if not enough data
        if len(self.window) < 2:
            return 0.0, 0.0

        # --- Normalized RMS ---
        rms_min, rms_max = np.min(self.rms_history), np.max(self.rms_history)
        if rms_max - rms_min > 1e-6:
            norm_rms = (rms - rms_min) / (rms_max - rms_min)
        else:
            norm_rms = 0.0
        norm_rms = np.clip(norm_rms, 0.0, 1.0)

        # --- Spectral Flux (Onset detection) ---
        spectrum = np.abs(np.fft.rfft(mono, n=self.block_size))
        mag = np.log1p(spectrum)  # Log compression
        diff = mag - self.prev_mag
        flux = np.sum(diff.clip(min=0))
        self.prev_mag = mag
        self.recent_flux.append(flux)
        self.flux_history.append(flux)

        # Normalize flux
        flux_min, flux_max = np.min(self.flux_history), np.max(self.flux_history)
        if flux_max - flux_min > 1e-6:
            norm_flux = (flux - flux_min) / (flux_max - flux_min)
        else:
            norm_flux = 0.0
        norm_flux = np.clip(norm_flux, 0.0, 1.0)

        # --- Beat Intensity ---
        if len(self.recent_flux) > 3:
            mean_flux = np.mean(self.recent_flux)
            std_flux = np.std(self.recent_flux)
        else:
            mean_flux, std_flux = 0.0, 0.0

        beat_intensity = 1.0 if flux > (mean_flux + 1.0 * std_flux) else 0.0

        # --- Weighted Combination ---
        w_rms = getattr(self.config.audio, "WEIGHT_RMS", 0.1)
        w_beat = getattr(self.config.audio, "WEIGHT_BEAT", 0.8)

        combined = (
            w_rms * norm_rms + w_beat * beat_intensity
        )
        combined = np.clip(combined, 0.0, 1.0)

        # --- Smooth transitions (EMA) ---
        self.smoothed_level = (
            self.smoothing * self.smoothed_level + (1 - self.smoothing) * combined
        )
        self.smoothed_level = np.clip(self.smoothed_level, 0.0, 1.0)

        # --- Gamma correction ---
        gamma = getattr(self.config.audio, "GAMMA", 1.1)
        raw_brightness = np.clip(norm_rms ** gamma, 0.0, 1.0)
        smoothed_brightness = np.clip(self.smoothed_level ** gamma, 0.0, 1.0)
        
        return float(raw_brightness), float(smoothed_brightness)

if __name__ == "__main__":
    # Example usage with dummy input
    audio_processor = AudioProcessor()

    for _ in range(10):
        dummy_data = np.random.randn(audio_processor.block_size, 2) * 0.01
        raw, brightness = audio_processor.process_audio(dummy_data)
        print(f"Brightness: {brightness:.4f}")
