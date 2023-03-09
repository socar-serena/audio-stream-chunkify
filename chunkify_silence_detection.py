import argparse
import os.path
from datetime import datetime

from audio_file_stream import AudioFileStream, write_wav_file


def main(
    wav_filename: str, silence_threshold: int, duration_threshold: int, output_dir: str
) -> None:
    """입력으로 들어온 파일을 읽어 정해진 길이대로 잘라 wav 파일을 저장한다."""

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with AudioFileStream(wav_filename=wav_filename) as (stream, wf):
        n_channels = wf.getnchannels()
        sampwidth = wf.getsampwidth()
        frame_rate = wf.getframerate()

        for audio_chunk_frames in stream.generate_by_silence_detection(
            silence_threshold=silence_threshold, duration_threshold=duration_threshold
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
    parser.add_argument("--silence_threshold", "-v", type=int, default=-30)
    parser.add_argument("--duration_threshold", "-s", type=int, default=1)
    parser.add_argument("--output_dir", "-o", type=str, default="outputs/silence")
    cfg = parser.parse_args()

    main(cfg.filename, cfg.silence_threshold, cfg.duration_threshold, cfg.output_dir)
