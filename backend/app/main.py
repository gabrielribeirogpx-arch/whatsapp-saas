from fastapi import FastAPI

from app.main import app as application

app = FastAPI()
app = application

__all__ = ["app"]
