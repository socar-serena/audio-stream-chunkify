import argparse
import os.path
import wave
from typing import Tuple
from datetime import datetime


def write_wav_file(
    filename: str, frames: bytes, n_channels: int, sampwidth: int, frame_rate: int
) -> str:
    """wav file을 저장한다."""

    chunk_wav_file = wave.open(filename, "wb")
    chunk_wav_file.setnchannels(n_channels)
    chunk_wav_file.setsampwidth(sampwidth)
    chunk_wav_file.setframerate(frame_rate)
    chunk_wav_file.writeframes(frames)
    chunk_wav_file.close()

    return filename


class AudioFileStream:
    def __init__(self, wav_filename: str):
        self._wav_filename = wav_filename

    def __enter__(self) -> Tuple["AudioFileStream", wave.Wave_read]:
        self._wav_file = wave.open(self._wav_filename, "rb")
        return self, self._wav_file

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._wav_file.close()

    def generate(self, chunk_seconds: int) -> bytes:
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


def main(wav_filename: str, chunk_seconds: int, output_dir: str) -> None:
    """입력으로 들어온 파일을 읽어 정해진 길이대로 잘라 wav 파일을 저장한다."""

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with AudioFileStream(wav_filename=wav_filename) as (stream, wf):
        n_channels = wf.getnchannels()
        sampwidth = wf.getsampwidth()
        frame_rate = wf.getframerate()

        for audio_chunk_frames in stream.generate(chunk_seconds=chunk_seconds):
            chunk_filename = os.path.join(
                output_dir, f"{datetime.utcnow()}_{wav_filename}"
            )
            write_wav_file(
                chunk_filename, audio_chunk_frames, n_channels, sampwidth, frame_rate
            )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--filename", "-f", type=str, required=True)
    parser.add_argument("--chunk_seconds", "-s", type=int, default=10)
    parser.add_argument("--output_dir", "-o", type=str, default="outputs")
    cfg = parser.parse_args()

    main(cfg.filename, cfg.chunk_seconds, cfg.output_dir)
