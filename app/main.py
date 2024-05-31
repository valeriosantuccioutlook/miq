import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from app.api.routers import user
from app.database.session import Base, engine
from app.depends.middlewares import RateLimitingMiddleware

# create tables from models
Base.metadata.create_all(bind=engine)

# instanciate app
app: FastAPI = FastAPI(
    title="MiQ",
    description="MiQ - Users Management",
    version="1",
    contact={
        "name": "Valerio Santucci",
        "email": "valerio.santucci@outlook.it",
    },
)

# compress response to limit bandwith
app.add_middleware(middleware_class=GZipMiddleware)

# add limit on requests per minutes
app.add_middleware(middleware_class=RateLimitingMiddleware)

# allow comunication with frontend if in different origins
app.add_middleware(
    middleware_class=CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)


# include routers
app.include_router(router=user.router, tags=["User"])

# add monitoring metrics source
Instrumentator().instrument(app=app).expose(app=app)

if __name__ == "__main__":
    uvicorn.run(app="app.main:app", reload=True, host="0.0.0.0", port=8000)
