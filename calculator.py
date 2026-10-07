"""Calculator interaction state, independent of Tkinter."""
import re
from engine import evaluate_scientific_expression, apply_function_expression, format_scientific_result


class Calculator:
    def __init__(self):
        self.expression = ""
        self.answer = 0
        self.result = "0"
        self.mode = "DEG"
        self.evaluated = False

    def append(self, token):
        if self.evaluated:
            self.expression = "Ans" if token in ("+", "-", "*", "/", "%", "**") else ""
            self.evaluated = False
        previous = self.expression
        if previous and (previous[-1].isdigit() or previous.endswith((")", "pi", "e", "Ans"))) and (
            token in ("(", "pi", "e", "Ans") or (token[0].isdigit() and previous.endswith((")", "pi", "e", "Ans")))
        ):
            token = "*" + token
        if len(previous + token) > 256:
            raise ValueError("Ekspresi maksimum 256 karakter.")
        self.expression += token

    def apply(self, name):
        value = apply_function_expression("Ans" if self.evaluated else self.expression, name)
        if len(value) > 256:
            raise ValueError("Ekspresi maksimum 256 karakter.")
        self.expression = value
        self.evaluated = False

    def clear(self):
        self.expression, self.result, self.evaluated = "", "0", False

    def backspace(self):
        if self.evaluated:
            self.clear()
            return
        self.expression = re.sub(r"(?:factorial|powten|square|sqrt|asin|acos|atan|sin|cos|tan|log|ln|exp|abs|inv|neg)\($|Ans$|pi$|\*\*$|.$", "", self.expression)

    def calculate(self):
        if self.expression:
            result = evaluate_scientific_expression(self.expression, angle_mode=self.mode, answer=self.answer)
            self.answer = result
            self.result = format_scientific_result(result)
            self.evaluated = True
