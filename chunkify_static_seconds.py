import argparse
import os.path
import wave
from datetime import datetime

from audio_file_stream import AudioFileStream


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


def main(wav_filename: str, chunk_seconds: int, output_dir: str) -> None:
    """입력으로 들어온 파일을 읽어 정해진 길이대로 잘라 wav 파일을 저장한다."""

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with AudioFileStream(wav_filename=wav_filename) as (stream, wf):
        n_channels = wf.getnchannels()
        sampwidth = wf.getsampwidth()
        frame_rate = wf.getframerate()

        for audio_chunk_frames in stream.generate_by_static_seconds(
            chunk_seconds=chunk_seconds
        ):
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
