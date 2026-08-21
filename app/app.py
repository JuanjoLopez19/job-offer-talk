from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1.__init_ import main_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(main_router)
