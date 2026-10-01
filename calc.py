import ast
import operator
import tkinter as tk

# Safe expression evaluator (avoids using eval on raw input)
OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Mod: operator.mod,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def safe_eval(expr):
    def _eval(node):
        if isinstance(node, ast.Expression):
            return _eval(node.body)
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value
        if isinstance(node, ast.BinOp) and type(node.op) in OPS:
            return OPS[type(node.op)](_eval(node.left), _eval(node.right))
        if isinstance(node, ast.UnaryOp) and type(node.op) in OPS:
            return OPS[type(node.op)](_eval(node.operand))
        raise ValueError("Invalid expression")

    return _eval(ast.parse(expr, mode="eval"))


class Calculator:
    def __init__(self, root):
        self.root = root
        self.root.title("Calculator")
        self.root.geometry("320x420")
        self.root.resizable(False, False)
        self.root.configure(bg="#1e1e1e")

        self.expression = ""

        # Display
        self.display = tk.Entry(
            root, font=("Arial", 26), justify="right", bd=0,
            bg="#2b2b2b", fg="white", insertbackground="white",
        )
        self.display.grid(row=0, column=0, columnspan=4, padx=10, pady=15, ipady=15, sticky="nsew")
        self.display.config(state="readonly", readonlybackground="#2b2b2b")

        # Button layout
        buttons = [
            ("C", "⌫", "%", "/"),
            ("7", "8", "9", "*"),
            ("4", "5", "6", "-"),
            ("1", "2", "3", "+"),
            ("±", "0", ".", "="),
        ]

        for r, row in enumerate(buttons, start=1):
            for c, label in enumerate(row):
                self.make_button(label, r, c)

        for i in range(4):
            root.columnconfigure(i, weight=1)
        for i in range(1, 6):
            root.rowconfigure(i, weight=1)

        # Keyboard support
        root.bind("<Key>", self.on_key)
        root.bind("<Return>", lambda e: self.press("="))
        root.bind("<BackSpace>", lambda e: self.press("⌫"))
        root.bind("<Escape>", lambda e: self.press("C"))

    def make_button(self, label, row, col):
        if label == "=":
            bg = "#ff9500"
        elif label in "/*-+%":
            bg = "#3a3a3a"
        elif label in ("C", "⌫", "±"):
            bg = "#555555"
        else:
            bg = "#444444"

        tk.Button(
            self.root, text=label, font=("Arial", 16), bg=bg, fg="white",
            activebackground="#666666", activeforeground="white",
            bd=0, command=lambda: self.press(label),
        ).grid(row=row, column=col, padx=4, pady=4, sticky="nsew")

    def set_display(self, text):
        self.display.config(state="normal")
        self.display.delete(0, tk.END)
        self.display.insert(0, text)
        self.display.config(state="readonly")

    def press(self, key):
        if key == "C":
            self.expression = ""
        elif key == "⌫":
            self.expression = self.expression[:-1]
        elif key == "±":
            if self.expression.startswith("-"):
                self.expression = self.expression[1:]
            elif self.expression:
                self.expression = "-" + self.expression
        elif key == "=":
            self.calculate()
            return
        else:
            self.expression += key
        self.set_display(self.expression)

    def calculate(self):
        if not self.expression:
            return
        try:
            result = safe_eval(self.expression)
            if isinstance(result, float) and result.is_integer():
                result = int(result)
            self.expression = str(round(result, 10)) if isinstance(result, float) else str(result)
            self.set_display(self.expression)
        except ZeroDivisionError:
            self.expression = ""
            self.set_display("Cannot divide by 0")
        except Exception:
            self.expression = ""
            self.set_display("Error")

    def on_key(self, event):
        if event.char in "0123456789.+-*/%":
            self.press(event.char)


if __name__ == "__main__":
    root = tk.Tk()
    Calculator(root)
    root.mainloop()
