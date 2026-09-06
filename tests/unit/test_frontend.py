from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.frontend import mount_frontend


def test_frontend_serves_index_for_client_side_routes(tmp_path: Path) -> None:
    index = tmp_path / "index.html"
    index.write_text("<h1>JobTalk</h1>", encoding="utf-8")
    app = FastAPI()
    mount_frontend(app, tmp_path)

    response = TestClient(app).get("/entrevista")

    assert response.status_code == 200
    assert "JobTalk" in response.text


def test_frontend_does_not_capture_unknown_api_routes(tmp_path: Path) -> None:
    (tmp_path / "index.html").write_text("JobTalk", encoding="utf-8")
    app = FastAPI()
    mount_frontend(app, tmp_path)

    assert TestClient(app).get("/v1/unknown").status_code == 404


def test_frontend_explains_when_build_is_missing(tmp_path: Path) -> None:
    app = FastAPI()
    mount_frontend(app, tmp_path)

    response = TestClient(app).get("/")

    assert response.status_code == 503
    assert "pnpm build" in response.text
