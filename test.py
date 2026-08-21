from pathlib import Path

from app.core.logger import get_logger, setup_logging
from app.services.stt.whisper_stt import WhisperSTT
from app.services.tts.kokoro_tts import KokoroTTS

setup_logging()
logger = get_logger()

INPUT_AUDIO = Path("samples/sample1.mp3")
OUTPUT_AUDIO = Path("output.wav")
STT_MODEL = "medium"
TTS_VOICE = "em_alex"


def main() -> None:
    logger.info("Starting the application")

    logger.info("Loading the STT and TTS services")
    stt = WhisperSTT()
    tts = KokoroTTS()

    logger.info("Loading the STT model")
    stt.load(STT_MODEL)
    logger.info("Loading the TTS voice")
    tts.load(TTS_VOICE)

    logger.info("Transcribing the audio")
    transcript = stt.transcribe_file(INPUT_AUDIO)
    logger.info(f"Transcript: {transcript}")

    logger.info("Generating the speech")
    speech = tts.generate(transcript)
    logger.info("Saving the speech")
    tts.save(speech, OUTPUT_AUDIO)
    logger.info(f"Speech saved to {OUTPUT_AUDIO}")


if __name__ == "__main__":
    main()
