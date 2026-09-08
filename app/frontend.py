from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

FRONTEND_DIST = Path(__file__).resolve().parents[1] / "frontend" / "dist"


def mount_frontend(app: FastAPI, dist_dir: Path = FRONTEND_DIST) -> None:
    """Serve the compiled React application without a second production server."""
    assets_dir = dist_dir / "assets"
    if assets_dir.is_dir():
        app.mount("/assets", StaticFiles(directory=assets_dir), name="frontend-assets")

    @app.get("/", include_in_schema=False)
    @app.get("/{frontend_path:path}", include_in_schema=False)
    async def serve_frontend(frontend_path: str = ""):
        if frontend_path == "v1" or frontend_path.startswith("v1/"):
            raise HTTPException(status_code=404)

        requested_file = (dist_dir / frontend_path).resolve()
        if dist_dir.resolve() in requested_file.parents and requested_file.is_file():
            return FileResponse(requested_file)

        index_file = dist_dir / "index.html"
        if index_file.is_file():
            return FileResponse(index_file)

        return HTMLResponse(
            "Frontend no compilado. Ejecuta `pnpm build` antes de iniciar FastAPI.",
            status_code=503,
        )
