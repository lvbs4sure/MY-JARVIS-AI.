"""Deterministic facial-control signals for a future identity-matched JARVIS rig.

This module does not animate a raster image. A reviewed VRM/glTF renderer must
map these normalized signals to real eyelid, gaze and facial blendshapes.
No camera, network, microphone, AI inference or background worker is used.
"""
from dataclasses import dataclass
import math

_STATES = frozenset({"ready", "listening", "thinking", "speaking", "paused", "error"})


def _finite(value, name):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(f"{name} must be a finite number")
    return float(value)


def _clamp(value, low, high):
    return max(low, min(high, value))


@dataclass(frozen=True)
class FacePose:
    """Normalized controls; blink=1 means eyes fully closed."""
    blink: float
    gaze_x: float
    gaze_y: float
    mouth_open: float
    expression: str


class FaceMotionController:
    """Clock-sampled facial motion, independent of render frame rate.

    Mouth movement is accepted only from an actual audio-clock LipTimeline.
    A rig mapping is required before any of these controls become visible.
    """

    def __init__(self, *, blink_interval_ms=4400, blink_duration_ms=180):
        self.blink_interval_ms = _finite(blink_interval_ms, "blink interval")
        self.blink_duration_ms = _finite(blink_duration_ms, "blink duration")
        if self.blink_interval_ms < 1000 or not 50 <= self.blink_duration_ms <= 600:
            raise ValueError("Invalid blink timing")

    def sample(self, elapsed_ms, *, state="ready", reduced_motion=False,
               timeline=None, audio_position_ms=0, audio_playing=False,
               interrupted=False):
        elapsed = _finite(elapsed_ms, "elapsed")
        if elapsed < 0:
            raise ValueError("Elapsed time cannot be negative")
        if state not in _STATES:
            raise ValueError("Unknown avatar state")
        if not isinstance(reduced_motion, bool) or not isinstance(audio_playing, bool):
            raise ValueError("Motion flags must be boolean")
        if not isinstance(interrupted, bool):
            raise ValueError("Interrupted flag must be boolean")

        if reduced_motion:
            return FacePose(0.0, 0.0, 0.0, 0.0, state)

        phase = elapsed % self.blink_interval_ms
        blink = 0.0
        if phase < self.blink_duration_ms:
            half = self.blink_duration_ms / 2
            blink = (phase / half if phase <= half
                     else (self.blink_duration_ms - phase) / half)
        # Small deterministic gaze shifts; no camera tracking or emotion inference.
        gaze_x = 0.16 * math.sin(elapsed / 2300)
        gaze_y = 0.08 * math.sin(elapsed / 3100)
        mouth = 0.0
        if state == "speaking" and audio_playing and not interrupted and timeline is not None:
            weights = timeline.sample(audio_position_ms, playing=True)
            # Neutral/silence viseme 0 is never interpreted as mouth movement.
            mouth = _clamp(1.0 - weights.get(0, 0.0), 0.0, 1.0)
        return FacePose(blink, gaze_x, gaze_y, mouth, state)
