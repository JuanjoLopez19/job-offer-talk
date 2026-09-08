import argparse
import asyncio
import json
from pathlib import Path
from typing import Any
from urllib.parse import quote, urlsplit, urlunsplit
from urllib.request import Request, urlopen

from websockets.asyncio.client import connect

THREAD_ID_HEADER = "X-Thread-ID"


def post_json(
    url: str,
    payload: Any,
    *,
    thread_id: str | None = None,
    timeout: float = 300,
) -> tuple[dict[str, Any], str | None]:
    headers = {"Content-Type": "application/json"}
    if thread_id:
        headers[THREAD_ID_HEADER] = thread_id

    request = Request(
        url,
        data=json.dumps(payload).encode(),
        headers=headers,
        method="POST",
    )
    with urlopen(request, timeout=timeout) as response:
        body = json.loads(response.read())
        return body, response.headers.get(THREAD_ID_HEADER)


def websocket_url(base_url: str, thread_id: str) -> str:
    parsed = urlsplit(base_url)
    scheme = "wss" if parsed.scheme == "https" else "ws"
    path = f"{parsed.path.rstrip('/')}/v1/conversation/{quote(thread_id, safe='')}"
    return urlunsplit((scheme, parsed.netloc, path, "", ""))


async def run_client(args: argparse.Namespace) -> None:
    graph_url = f"{args.base_url.rstrip('/')}/v1/graph/"

    print("Iniciando conversación...")
    initial_result, thread_id = await asyncio.to_thread(post_json, graph_url, {})
    if not thread_id:
        raise RuntimeError(f"La respuesta no incluye {THREAD_ID_HEADER}")

    print(f"Thread ID: {thread_id}")
    if message := initial_result.get("assistant_message"):
        print(f"Asistente: {message}")

    offer_url = args.offer_url or input("URL de la oferta: ").strip()
    if not offer_url:
        raise ValueError("La URL de la oferta no puede estar vacía")

    ws_url = websocket_url(args.base_url, thread_id)
    async with connect(ws_url) as websocket:
        print(f"WebSocket conectado: {ws_url}")
        result, returned_thread_id = await asyncio.to_thread(
            post_json,
            graph_url,
            offer_url,
            thread_id=thread_id,
        )

        if returned_thread_id != thread_id:
            raise RuntimeError("La API devolvió un thread ID diferente")

        print(json.dumps(result, indent=2, ensure_ascii=False))
        if not result.get("is_tts_message"):
            print("La respuesta no solicitó generación TTS.")
            return

        metadata_frame = await asyncio.wait_for(
            websocket.recv(), timeout=args.ws_timeout
        )
        audio_frame = await asyncio.wait_for(websocket.recv(), timeout=args.ws_timeout)
        if not isinstance(metadata_frame, str) or not isinstance(audio_frame, bytes):
            raise RuntimeError("El WebSocket devolvió frames en un orden inesperado")

        metadata = json.loads(metadata_frame)
        output_path = Path(args.output)
        output_path.write_bytes(audio_frame)
        print(f"Metadatos TTS: {json.dumps(metadata, ensure_ascii=False)}")
        print(f"Audio guardado en: {output_path.resolve()}")

        await websocket.send(
            json.dumps(
                {
                    "event": "user_message",
                    "content_type": metadata.get("content_type", "audio/wav"),
                }
            )
        )
        await websocket.send(audio_frame)

        transcription_frame = await asyncio.wait_for(
            websocket.recv(), timeout=args.ws_timeout
        )
        if not isinstance(transcription_frame, str):
            raise RuntimeError("La transcripción no se recibió como un frame JSON")

        transcription = json.loads(transcription_frame)
        print(f"Transcripción STT: {json.dumps(transcription, ensure_ascii=False)}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Prueba el flujo HTTP + WebSocket de una conversación."
    )
    parser.add_argument(
        "offer_url",
        nargs="?",
        help="URL de la oferta; se solicita de forma interactiva si se omite.",
    )
    parser.add_argument(
        "--base-url",
        default="http://127.0.0.1:8000",
        help="URL base de la API.",
    )
    parser.add_argument(
        "--output",
        default="output.wav",
        help="Archivo donde guardar el audio recibido.",
    )
    parser.add_argument(
        "--ws-timeout",
        type=float,
        default=30,
        help="Segundos de espera para cada frame WebSocket.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    asyncio.run(run_client(parse_args()))
