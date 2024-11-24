# pylint: disable=C0415
# pylint: disable=unused-import
"""CLI entrypoint."""

import asyncclick as click

from fluctlight.logger import get_logger

logger = get_logger(__name__)


@click.group()
def main() -> None:
    pass


@main.command()
async def start() -> None:
    from fluctlight.server import start_server

    logger.debug("Debug log is on[if you see this]")
    start_server()


# Backdoor testing code block
@main.command()
async def backdoor() -> None:
    from fluctlight.audio.text_to_speech import get_text_to_speech

    tts = get_text_to_speech()
    wave_data = await tts.generate_audio(
        text="""
hello, how are you?"""
    )
    logger.info("wave data length", length=len(wave_data))
    save_wave_data_pydub("/tmp/output.wav", wave_data)


# Function to save wave_data using pydub
def save_wave_data_pydub(file_name, data):
    from pydub import AudioSegment

    # Create an AudioSegment instance from raw audio data
    audio_segment = AudioSegment(
        data=data,
        sample_width=2,  # Assuming 2 bytes for 16-bit audio
        frame_rate=16000,  # Specified frame rate
        channels=1,  # Mono audio
    )
    # Export the audio segment to a WAV file
    audio_segment.export(file_name, format="wav")
