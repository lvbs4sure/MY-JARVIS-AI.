"""Audio-clock driven viseme cues for a future approved character rig.

No rendering, synthesis, model download, camera access or background inference.
Input offsets must come from the same audio clip that is played to the user.
"""
from bisect import bisect_right
from dataclasses import dataclass
import math


def _time(value):
    if isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value) or value<0:
        raise ValueError("Audio times must be finite, nonnegative milliseconds.")
    return float(value)


@dataclass(frozen=True)
class VisemeCue:
    offset_ms: float
    duration_ms: float
    viseme: int

    def __post_init__(self):
        _time(self.offset_ms)
        _time(self.duration_ms)
        if isinstance(self.viseme,bool) or not isinstance(self.viseme,int) or not 0<=self.viseme<=21:
            raise ValueError("SAPI viseme must be an integer from 0 to 21.")


class LipTimeline:
    """Pure sampling; seeks and frame skips never accumulate timer drift."""
    def __init__(self,cues,clip_duration_ms,transition_ms=40):
        self.duration=_time(clip_duration_ms)
        self.transition=_time(transition_ms)
        if len(cues)>20000:
            raise ValueError("Viseme timeline is too large.")
        self.cues=tuple(cues)
        previous=-1
        for cue in self.cues:
            if not isinstance(cue,VisemeCue):
                raise ValueError("Expected validated viseme cues.")
            if cue.offset_ms<previous or cue.offset_ms+cue.duration_ms>self.duration:
                raise ValueError("Viseme cues must be ordered and inside the audio clip.")
            previous=cue.offset_ms
        self.offsets=tuple(cue.offset_ms for cue in self.cues)

    def sample(self,audio_position_ms,*,playing=False,interrupted=False):
        """Return normalized SAPI mouth weights. 0 is closed/silent.

        Feed the playback element's currentTime, not wall time or text length.
        A renderer must map these IDs to its own approved facial shapes.
        """
        position=_time(audio_position_ms)
        if not playing or interrupted or position>=self.duration:
            return {0:1.0}
        index=bisect_right(self.offsets,position)-1
        if index<0:return {0:1.0}
        cue=self.cues[index]
        if position>=cue.offset_ms+cue.duration_ms:return {0:1.0}
        previous=0
        if index>0:
            older=self.cues[index-1]
            if older.offset_ms+older.duration_ms>=cue.offset_ms:
                previous=older.viseme
        ramp=min(self.transition,cue.duration_ms/2)
        weight=1.0 if ramp==0 else min(1.0,(position-cue.offset_ms)/ramp)
        if previous==cue.viseme or weight>=1:return {cue.viseme:1.0}
        if weight<=0:return {previous:1.0}
        return {previous:1-weight,cue.viseme:weight}


def from_sapi_events(events,clip_duration_ms):
    """Accept only timing/type fields; no text, paths or provider credentials."""
    if not isinstance(events,list) or len(events)>20000:
        raise ValueError("Invalid viseme event list.")
    cues=[]
    for event in events:
        if not isinstance(event,dict) or set(event)!={"offset_ms","duration_ms","viseme"}:
            raise ValueError("Invalid viseme event fields.")
        cues.append(VisemeCue(event["offset_ms"],event["duration_ms"],event["viseme"]))
    return LipTimeline(cues,clip_duration_ms)
