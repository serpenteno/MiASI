import copy
from devices import DEFAULT_DEVICES
import antlr4
from gen.SmartHomeLexer import SmartHomeLexer
from gen.SmartHomeParser import SmartHomeParser
from InterpreterVisitor import InterpreterVisitor

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

    devices = copy.deepcopy(DEFAULT_DEVICES)

    print("\n=== DEVICES' INITIAL STATE ===")
    for device, props in devices.items():
        print(f"{device}: {props}")

    input_stream = antlr4.InputStream(code)
    lexer = SmartHomeLexer(input_stream)
    stream = antlr4.CommonTokenStream(lexer)
    parser = SmartHomeParser(stream)
    tree = parser.program()

    if parser.getNumberOfSyntaxErrors() > 0:
        print("Syntax error")
    else:
        interpreter = InterpreterVisitor(devices)
        interpreter.visit(tree)

        print("\n=== LOG ===")
        for entry in interpreter.log:
            print(entry)

        print("\n=== DEVICES' FINAL STATE ===")
        for device, props in interpreter.devices.items():
            print(f"{device}: {props}")