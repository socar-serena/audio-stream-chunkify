import wave
from typing import Tuple


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
            data = self._wav_file.readframes(self._wav_file.getframerate())
            _chunk_frames.append(data)

            if len(_chunk_frames) == chunk_seconds:
                yield b"".join(_chunk_frames)
                _chunk_frames = []

        yield b"".join(_chunk_frames)

    def generate_by_silence_detection(
        self, volume_threshold: int, duration_threshold: int
    ) -> bytes:
        """발화의 시작과 끝을 감지해 음성 스트림을 잘라낸다."""

        raise NotImplementedError
