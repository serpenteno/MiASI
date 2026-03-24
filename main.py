import antlr4
from gen.SmartHomeLexer import SmartHomeLexer
from gen.SmartHomeParser import SmartHomeParser
from InterpreterVisitor import InterpreterVisitor
from devices import DEFAULT_DEVICES


def run_code(code: str, devices: dict) -> dict:
    input_stream = antlr4.InputStream(code)
    lexer = SmartHomeLexer(input_stream)
    stream = antlr4.CommonTokenStream(lexer)
    parser = SmartHomeParser(stream)

    tree = parser.program()

    if parser.getNumberOfSyntaxErrors() > 0:
        return {"error": "Syntax error", "devices": devices, "log": []}

    interpreter = InterpreterVisitor(devices)
    interpreter.visit(tree)

    return {
        "devices": interpreter.devices,
        "log": interpreter.log,
        "error": None
    }


if __name__ == "__main__":
    code = """
    for room in [bathroom, kitchen] {
        set room.temp = 22;
    }
    
    if (living_room.window is open) {
        ignore living_room.temp;
    } else {
        set living_room.temp = 21;
    }

    turn on living_room.light;
    """

    initial_state = DEFAULT_DEVICES.copy()

    print("\n=== DEVICES' INITIAL STATE ===")
    for device, props in initial_state.items():
        print(f"{device}: {props}")

    result = run_code(code, initial_state)

    print("\n=== LOG ===")
    for entry in result["log"]:
        print(entry)

    print("\n=== DEVICES' FINAL STATE ===")
    for device, props in result["devices"].items():
        print(f"{device}: {props}")
