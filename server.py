from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from InterpreterVisitor import InterpreterVisitor
from pydantic import BaseModel
import copy
from devices import DEFAULT_DEVICES
import antlr4
from gen.SmartHomeLexer import SmartHomeLexer
from gen.SmartHomeParser import SmartHomeParser

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
    allow_credentials=False,
)

current_interpreter: InterpreterVisitor = None


class RunRequest(BaseModel):
    code: str


class SensorUpdate(BaseModel):
    device: str
    prop: str
    value: float | str


@app.post("/run")
def run(req: RunRequest):
    global current_interpreter

    devices = copy.deepcopy(DEFAULT_DEVICES)

    input_stream = antlr4.InputStream(req.code)
    lexer = SmartHomeLexer(input_stream)
    stream = antlr4.CommonTokenStream(lexer)
    parser = SmartHomeParser(stream)
    tree = parser.program()

    if parser.getNumberOfSyntaxErrors() > 0:
        return {"error": "Syntax error", "devices": devices, "log": []}

    current_interpreter = InterpreterVisitor(devices)
    current_interpreter.visit(tree)

    return {
        "devices": current_interpreter.devices,
        "log": current_interpreter.log,
        "error": None
    }

@app.get("/devices")
def get_devices():
    if current_interpreter is None:
        return DEFAULT_DEVICES
    return current_interpreter.devices

@app.post("/sensor")
def update_sensor(req: SensorUpdate):
    if current_interpreter is None:
        return {"error": "No program running. Call /run first."}
    if req.device not in current_interpreter.devices:
        return {"error": f"Unknown device: {req.device}"}
    if req.prop not in current_interpreter.devices[req.device]:
        return {"error": f"Unknown property: {req.prop}"}

    current_interpreter.devices[req.device][req.prop]["read"] = req.value
    current_interpreter._check_pending_rules()

    return {
        "ok": True,
        "device": req.device,
        "prop": req.prop,
        "read": req.value,
        "log": current_interpreter.log,
        "devices": current_interpreter.devices,
    }
