import wave
from typing import Tuple

import pydub
from pydub import silence


def write_wav_file(
    filename: str, frames: bytes, n_channels: int, sampwidth: int, frame_rate: int
) -> str:
    """wav file을 저장한다."""

    with wave.open(filename, "wb") as wf:
        wf.setnchannels(n_channels)
        wf.setsampwidth(sampwidth)
        wf.setframerate(frame_rate)
        wf.writeframes(frames)

    return filename


class AudioFileStream:
    def __init__(self, wav_filename: str):
        self._wav_filename = wav_filename

    def __enter__(self) -> Tuple["AudioFileStream", wave.Wave_read]:
        self._wav_file = wave.open(self._wav_filename, "rb")
        return self, self._wav_file

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._wav_file.close()

    def generate_by_static_seconds(self, chunk_seconds: int) -> bytes:
        """정해진 chunk_seconds에 맞게 음성 스트림을 잘라낸다."""

        _chunk_frames = []
        data = self._wav_file.readframes(self._wav_file.getframerate())
        while data:
            _chunk_frames.append(data)
            if len(_chunk_frames) == chunk_seconds:
                yield b"".join(_chunk_frames)
                _chunk_frames = []
            data = self._wav_file.readframes(self._wav_file.getframerate())

        yield b"".join(_chunk_frames)

    def generate_by_silence_detection(
        self, silence_threshold: int, duration_threshold: int
    ) -> bytes:
        """발화의 시작과 끝을 감지해 음성 스트림을 잘라낸다."""

        _chunk_frames = []
        _nonsilence_flags = []
        data = self._wav_file.readframes(self._wav_file.getframerate())

        is_started = False
        while data:  # 초단위로 nonsilence를 감지한다.
            segment = pydub.AudioSegment(
                data,
                sample_width=self._wav_file.getsampwidth(),
                channels=self._wav_file.getnchannels(),
                frame_rate=self._wav_file.getframerate(),
            )
            nonsilent = (
                silence.detect_nonsilent(segment, silence_thresh=silence_threshold)
                != []
            )

            if not is_started and nonsilent:
                is_started = True

            if is_started:
                _chunk_frames.append(data)
                _nonsilence_flags.append(nonsilent)

            if (
                len(_nonsilence_flags) >= duration_threshold
                and sum(_nonsilence_flags[-duration_threshold:]) == 0
            ):
                yield b"".join(_chunk_frames)
                _chunk_frames = []
                _nonsilence_flags = []
                is_started = False

            data = self._wav_file.readframes(self._wav_file.getframerate())

        yield b"".join(_chunk_frames)
