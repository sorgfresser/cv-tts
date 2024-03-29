from pydub import AudioSegment, silence
from src.parse.clip import Clip
from copy import copy
from pathlib import Path

SAMPLE_RATE = 16000  # 16kHz, same as paper
dBFS = -50  # same as paper


def mp3_to_wav(clip: Clip, output_dir: Path | None = None) -> Clip:
    audio_seg = AudioSegment.from_mp3(clip.filepath)
    audio_seg.set_frame_rate(16000)
    filepath = clip.filepath if output_dir is None else output_dir / clip.filepath.name
    audio_seg.export(filepath.with_suffix(".wav"), format="wav")
    updated = copy(clip)
    updated.filepath = filepath.with_suffix(".wav")
    return updated


def remove_silence(clip: Clip) -> None:
    """
    Remove leading and trailing silence from the clip. Will overwrite the original file and modify the clip in place.

    :param clip: The clip to remove silence from
    :return: None
    """
    audio_seg = AudioSegment.from_wav(clip.filepath)
    leading_silence = silence.detect_leading_silence(
        audio_seg, silence_threshold=dBFS, chunk_size=1
    )
    ending_silence = silence.detect_leading_silence(
        audio_seg.reverse(), silence_threshold=dBFS, chunk_size=1
    )
    audio_seg = audio_seg[leading_silence:-ending_silence]
    audio_seg.export(clip.filepath, format="wav")
    clip.duration_ms = len(audio_seg)
