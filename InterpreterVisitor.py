from gen.SmartHomeParser import SmartHomeParser
from gen.SmartHomeVisitor import SmartHomeVisitor


class InterpreterVisitor(SmartHomeVisitor):
    def __init__(self, devices: dict):
        self.devices = devices
        self.variables = {}
        self.ignored = set()
        self.log = []
        self.pending_rules = []

    def visitProgram(self, ctx: SmartHomeParser.ProgramContext):
        for statement in ctx.statement():
            self.visit(statement)
        return self.devices

    def visitStatement(self, ctx: SmartHomeParser.StatementContext):
        return self.visitChildren(ctx)

    def visitIfStatement(self, ctx: SmartHomeParser.IfStatementContext):
        result = self.visit(ctx.condition())
        if result:
            self.visit(ctx.ifBlock())
        elif ctx.elseBlock():
            self.visit(ctx.elseBlock())

    def visitIfBlock(self, ctx: SmartHomeParser.IfBlockContext):
        for statement in ctx.statement():
            self.visit(statement)

    def visitElseBlock(self, ctx: SmartHomeParser.ElseBlockContext):
        for statement in ctx.statement():
            self.visit(statement)

    def visitWhenStatement(self, ctx: SmartHomeParser.WhenStatementContext):
        self.pending_rules.append(ctx)
        self.log.append(f"rule for '{ctx.condition().getText()}' registered")

    def visitForStatement(self, ctx: SmartHomeParser.ForStatementContext):
        name = ctx.ID().getText()
        rooms = [id.getText() for id in ctx.roomList().ID()]
        for room in rooms:
            self.variables[name] = room
            for statement in ctx.statement():
                self.visit(statement)
            del self.variables[name]

    def visitStateCondition(self, ctx: SmartHomeParser.StateConditionContext):
        device = self._resolve(ctx.device().getText())
        prop = ctx.property_().getText()
        expected = ctx.STATE().getText()

        value_source = "set"
        if ctx.READ() is not None:
            value_source = "read"

        actual = self.devices.get(device, {}).get(prop, {}).get(value_source)
        return actual == expected

    def visitCompareCondition(self, ctx: SmartHomeParser.CompareConditionContext):
        device = self._resolve(ctx.device().getText())
        prop = ctx.property_().getText()
        op = ctx.COMPARE().getText()
        number = float(ctx.NUMBER().getText())

        value_source = "set"
        if ctx.READ() is not None:
            value_source = "read"

        actual = self.devices.get(device, {}).get(prop, 0).get(value_source)
        ops = {'>': actual > number, '>=': actual >= number,
               '<': actual < number, '<=': actual <= number,
               '==': actual == number, '!=': actual != number}
        return ops.get(op, False)

    def visitSetCommand(self, ctx: SmartHomeParser.SetCommandContext):
        device = self._resolve(ctx.device().getText())
        prop = ctx.property_().getText()
        key = f"{device}.{prop}"

        if key in self.ignored:
            self.log.append(f"{key} skipped (ignore active)")
            return

        raw = ctx.value()
        if raw.NUMBER():
            val = float(raw.NUMBER().getText())
            val = int(val) if val == int(val) else val
        else:
            val = raw.STATE().getText()

        if device not in self.devices:
            self.devices[device] = {}
        if prop not in self.devices[device]:
            self.devices[device][prop] = {"set": None, "read": None}
        self.devices[device][prop]["set"] = val
        self.log.append(f"{device}.{prop} = {val}")

        for rule in self.pending_rules[:]:
            if self.visit(rule.condition()):
                self.pending_rules.remove(rule)
                for statement in rule.statement():
                    self.visit(statement)

    def visitSetRelativeCommand(self, ctx: SmartHomeParser.SetRelativeCommandContext):
        device = self._resolve(ctx.device().getText())
        prop = ctx.property_().getText()
        key = f"{device}.{prop}"

        if key in self.ignored:
            self.log.append(f"{key} skipped (ignore active)")
            return

        number = float(ctx.NUMBER().getText())
        op = ctx.COMPUND_ASSIGN().getText()

        value_source = "set"
        if ctx.READ() is not None:
            value_source = "read"

        current = self.devices.get(device, {}).get(prop, {}).get(value_source)

        ops = {
            '+=': current + number,
            '-=': current - number,
            '*=': current * number,
            '/=': current / number if number != 0 else current,
        }

        val = ops[op]
        val = int(val) if val == int(val) else val

        self.devices[device][prop]["set"] = val
        self.log.append(f"{device}.{prop} {op} {number} -> {val}")

        for rule in self.pending_rules[:]:
            if self.visit(rule.condition()):
                self.pending_rules.remove(rule)
                for statement in rule.statement():
                    self.visit(statement)

    def visitReadCommand(self, ctx: SmartHomeParser.ReadCommandContext):
        device = self._resolve(ctx.device().getText())
        prop = ctx.property_().getText()
        val = self.devices.get(device, {}).get(prop, {}).get("read")
        self.log.append(f"read {device}.{prop} = {val}")

    def visitLightCommand(self, ctx: SmartHomeParser.LightCommandContext):
        device = self._resolve(ctx.device().getText())
        state = ctx.onOff().getText()

        if device not in self.devices:
            self.devices[device] = {}
        if "light" not in self.devices[device]:
            self.devices[device]["light"] = {"set": None, "read": None}
        self.devices[device]["light"]["set"] = state
        self.log.append(f"turn {state} {device}.light")

    def visitIgnoreCommand(self, ctx: SmartHomeParser.IgnoreCommandContext):
        device = self._resolve(ctx.device().getText())
        prop = ctx.property_().getText()
        key = f"{device}.{prop}"
        self.ignored.add(key)
        self.log.append(f"ignore {key}")

    def visitUnignoreCommand(self, ctx: SmartHomeParser.UnignoreCommandContext):
        device = self._resolve(ctx.device().getText())
        prop = ctx.property_().getText()
        key = f"{device}.{prop}"
        self.ignored.remove(key)
        self.log.append(f"unignore {key}")

    def _resolve(self, name: str):
        return self.variables.get(name, name)
