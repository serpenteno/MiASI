from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from main import run_code
from devices import DEFAULT_DEVICES


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
    allow_credentials=False,
)

class RunRequest(BaseModel):
    code: str
    devices: dict = None

@app.post("/run")
def run(req: RunRequest):
    devices = req.devices if req.devices else DEFAULT_DEVICES.copy()
    return run_code(req.code, devices)

@app.get("/devices")
def get_devices():
    return DEFAULT_DEVICES
