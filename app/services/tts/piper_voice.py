from pathlib import Path
from urllib.request import urlopen

PIPER_VOICE_BASE_URL = (
    "https://huggingface.co/rhasspy/piper-voices/resolve/main/es/es_ES/"
    "davefx/medium"
)
DEFAULT_PIPER_VOICE = "es_ES-davefx-medium"


def ensure_piper_voice(
    voice_name: str,
    model_dir: str | Path,
) -> Path:
    model_path = Path(voice_name).expanduser()
    if model_path.suffix == ".onnx":
        _validate_voice_files(model_path)
        return model_path

    target_dir = Path(model_dir).expanduser()
    target_dir.mkdir(parents=True, exist_ok=True)
    model_path = target_dir / f"{voice_name}.onnx"
    config_path = model_path.with_suffix(".onnx.json")

    if model_path.is_file() and config_path.is_file():
        return model_path

    relative_path = f"{voice_name}.onnx"
    _download_file(f"{PIPER_VOICE_BASE_URL}/{relative_path}", model_path)
    _download_file(f"{PIPER_VOICE_BASE_URL}/{relative_path}.json", config_path)
    _validate_voice_files(model_path)
    return model_path


def _download_file(url: str, destination: Path) -> None:
    temporary_path = destination.with_suffix(f"{destination.suffix}.tmp")
    try:
        with urlopen(url, timeout=60) as response, temporary_path.open("wb") as file:
            while chunk := response.read(1024 * 1024):
                file.write(chunk)
        temporary_path.replace(destination)
    except Exception:
        temporary_path.unlink(missing_ok=True)
        raise


def _validate_voice_files(model_path: Path) -> None:
    config_path = model_path.with_suffix(".onnx.json")
    if not model_path.is_file() or not config_path.is_file():
        raise FileNotFoundError(
            f"Piper voice requires both {model_path} and {config_path}"
        )
