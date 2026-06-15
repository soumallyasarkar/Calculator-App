import sys
import ast
import operator as op
import ctypes

from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QGridLayout,
    QPushButton,
    QLineEdit,
    QSizePolicy
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon

# ---------------- Safe Expression Evaluator ---------------- #

ALLOWED_OPERATORS = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.Pow: op.pow,
    ast.USub: op.neg,
    ast.UAdd: op.pos,
}


def safe_eval(expression):
    def evaluate(node):
        if isinstance(node, ast.Expression):
            return evaluate(node.body)

        elif isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float)):
                return node.value
            raise ValueError("Invalid constant")

        elif isinstance(node, ast.Num):
            return node.n

        elif isinstance(node, ast.BinOp):
            left = evaluate(node.left)
            right = evaluate(node.right)

            operator = type(node.op)
            if operator not in ALLOWED_OPERATORS:
                raise ValueError("Operator not allowed")

            return ALLOWED_OPERATORS[operator](left, right)

        elif isinstance(node, ast.UnaryOp):
            operand = evaluate(node.operand)

            operator = type(node.op)
            if operator not in ALLOWED_OPERATORS:
                raise ValueError("Operator not allowed")

            return ALLOWED_OPERATORS[operator](operand)

        raise ValueError("Invalid expression")

    tree = ast.parse(expression, mode="eval")
    return evaluate(tree)


# ---------------- Calculator ---------------- #

class Calculator(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Calculator")
        self.setWindowIcon(QIcon("calculator.ico"))
        self.resize(380, 600)
        self.setMinimumSize(320, 500)

        self.init_ui()
        self.apply_theme()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(12)

        # Display
        self.display = QLineEdit("0")
        self.display.setReadOnly(True)
        self.display.setAlignment(Qt.AlignRight)
        self.display.setFont(QFont("Arial", 28))
        self.display.setMinimumHeight(80)

        main_layout.addWidget(self.display)

        grid = QGridLayout()
        grid.setSpacing(10)

        buttons = [
            ['C', '⌫', '%', '/'],
            ['7', '8', '9', '*'],
            ['4', '5', '6', '-'],
            ['1', '2', '3', '+'],
            ['(', '0', ')', '.']
        ]

        for row, values in enumerate(buttons):
            for col, text in enumerate(values):
                button = QPushButton(text)

                button.setFont(QFont("Arial", 20))
                button.setSizePolicy(
                    QSizePolicy.Expanding,
                    QSizePolicy.Expanding
                )

                button.clicked.connect(self.button_clicked)

                grid.addWidget(button, row, col)

        # Equal button
        self.equal_button = QPushButton("=")

        self.equal_button.setFont(QFont("Arial", 22))
        self.equal_button.setObjectName("equalButton")

        self.equal_button.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Expanding
        )

        self.equal_button.clicked.connect(self.calculate)

        grid.addWidget(self.equal_button, 5, 0, 1, 4)

        # Responsive resizing
        for i in range(4):
            grid.setColumnStretch(i, 1)

        for i in range(6):
            grid.setRowStretch(i, 1)

        main_layout.addLayout(grid)

    def apply_theme(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #121212;
                color: white;
            }

            QLineEdit {
                background-color: #1E1E1E;
                border: 1px solid #2E2E2E;
                border-radius: 18px;
                color: white;
                padding: 15px;
            }

            QPushButton {
                background-color: #2A2A2A;
                border: 1px solid #3A3A3A;
                border-radius: 16px;
                color: white;
            }

            QPushButton:hover {
                background-color: #353535;
            }

            QPushButton:pressed {
                background-color: #454545;
            }

            QPushButton#equalButton {
                background-color: #4F8BD6;
                border: none;
                font-weight: bold;
            }

            QPushButton#equalButton:hover {
                background-color: #5C98E5;
            }

            QPushButton#equalButton:pressed {
                background-color: #3F79C4;
            }
        """)

    def button_clicked(self):
        text = self.sender().text()

        current = self.display.text()

        if current == "0":
            current = ""

        if text == 'C':
            self.display.setText("0")

        elif text == '⌫':
            current = current[:-1]

            if current == "":
                current = "0"

            self.display.setText(current)

        else:
            self.display.setText(current + text)

    def calculate(self):
        expression = self.display.text()

        try:
            expression = expression.replace('%', '/100')

            result = safe_eval(expression)

            if isinstance(result, float):
                result = round(result, 10)

                if result.is_integer():
                    result = int(result)

            self.display.setText(str(result))

        except Exception:
            self.display.setText("Error")

    def keyPressEvent(self, event):
        key = event.key()
        text = event.text()

        current = self.display.text()

        if current == "0":
            current = ""

        if key in (Qt.Key_Return, Qt.Key_Enter):
            self.calculate()

        elif key == Qt.Key_Backspace:
            current = current[:-1]

            if current == "":
                current = "0"

            self.display.setText(current)

        elif key == Qt.Key_Escape:
            self.display.setText("0")

        elif text in '0123456789+-*/().%':
            self.display.setText(current + text)

        else:
            super().keyPressEvent(event)

    def showEvent(self, event):
        super().showEvent(event)
        self.enable_dark_title_bar()

    def enable_dark_title_bar(self):
        """
        Enable native dark title bar on Windows 10/11.
        """

        if sys.platform != "win32":
            return

        try:
            hwnd = int(self.winId())

            DWMWA_USE_IMMERSIVE_DARK_MODE = 20
            value = ctypes.c_int(1)

            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                hwnd,
                DWMWA_USE_IMMERSIVE_DARK_MODE,
                ctypes.byref(value),
                ctypes.sizeof(value)
            )

        except Exception:
            pass


# ---------------- Main ---------------- #

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("calculator.ico"))
    window = Calculator()
    window.show()

    sys.exit(app.exec_())