import tkinter as tk
import operator as op

# Variables
UI_FONT = "Helvetica"
SCREEN_TEXT_SIZE = 40
KEY_TEXT_SIZE = 20

BACKSPACE = "DEL"

KEYPAD_GRID = [
    ["C", "±", "%", "÷"],
    ["7", "8", "9", "×"],
    ["4", "5", "6", "-"],
    ["1", "2", "3", "+"],
    ["0", ".", BACKSPACE, "="]
]

OPERATIONS = {
    "+": op.add,
    "-": op.sub,
    "×": op.mul,
    "÷": lambda x, y: x / y if y != 0 else "Error"
}


class CalculatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Calculator")
        self.root.resizable(False, False)

        self.first_val = None
        self.active_op = None
        self.reset_next = False
        self.display_var = tk.StringVar(value="0")

        self._build_interface()
        self._center_on_screen()

    def _build_interface(self):
        container = tk.Frame(self.root, padx=8, pady=8)
        container.pack()

        total_cols = len(KEYPAD_GRID)

        screen = tk.Label(
            container,
            textvariable=self.display_var,
            font=(UI_FONT, SCREEN_TEXT_SIZE),
            anchor="e",
            padx=6
        )
        screen.grid(row=0, column=0, columnspan=total_cols, sticky="we", pady=(0, 8))

        for r_idx, row_items in enumerate(KEYPAD_GRID):
            for c_idx, key_text in enumerate(row_items):
                btn = tk.Button(
                    container,
                    text=key_text,
                    font=(UI_FONT, KEY_TEXT_SIZE),
                    width=4,
                    height=1,
                    command=lambda k=key_text: self._on_key_press(k)
                )
                btn.grid(row=r_idx + 1, column=c_idx, padx=2, pady=2)

    def _clean_output(self, number):
        if isinstance(number, str):
            return number
        rounded = round(number, 10)
        return str(int(rounded)) if rounded.is_integer() else str(rounded)

    def _on_key_press(self, key):
        current = self.display_var.get()

        if current == "Error" and key != "C":
            return

        if key == "C":
            self.first_val = None
            self.active_op = None
            self.reset_next = False
            self.display_var.set("0")

        elif key == BACKSPACE:
            if len(current) > 1 and not (len(current) == 2 and current.startswith("-")):
                self.display_var.set(current[:-1])
            else:
                self.display_var.set("0")

        elif key == "±":
            if current != "0":
                val = float(current) * -1
                self.display_var.set(self._clean_output(val))

        elif key == "%":
            val = float(current) / 100
            self.display_var.set(self._clean_output(val))

        elif key == ".":
            if self.reset_next:
                self.display_var.set("0.")
                self.reset_next = False
            elif "." not in current:
                self.display_var.set(current + ".")

        elif key.isdigit():
            if current == "0" or self.reset_next:
                self.display_var.set(key)
                self.reset_next = False
            else:
                self.display_var.set(current + key)

        elif key in OPERATIONS:
            self.first_val = float(current)
            self.active_op = key
            self.reset_next = True

        elif key == "=":
            if self.first_val is not None and self.active_op is not None:
                second_val = float(current)
                math_func = OPERATIONS[self.active_op]
                answer = math_func(self.first_val, second_val)

                self.display_var.set(self._clean_output(answer))
                self.first_val = None
                self.active_op = None
                self.reset_next = True

    def _center_on_screen(self):
        self.root.update_idletasks()
        w = self.root.winfo_width()
        h = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (w // 2)
        y = (self.root.winfo_screenheight() // 2) - (h // 2)
        self.root.geometry(f"+{x}+{y}")


if __name__ == "__main__":
    app_window = tk.Tk()
    CalculatorApp(app_window)
    app_window.mainloop()
