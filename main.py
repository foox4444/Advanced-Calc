import tkinter as tk
import operator as op
import math

# Variables
UI_FONT = "Helvetica"
SCREEN_TEXT_SIZE = 40
KEY_TEXT_SIZE = 18
PREVIEW_TEXT_SIZE = 14

BACKSPACE = "DEL"

KEYPAD_GRID = [
    ["MC", "MR", "M+", "M-"],
    ["√", "x²", "1/x", "HIST"],
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
    "÷": lambda x, y: x / y if y != 0 else "Error",
    "^": op.pow
}


class CalculatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Calculator")
        self.root.resizable(False, False)

        self.first_val = None
        self.active_op = None
        self.reset_next = False
        self.memory = 0.0
        self.history = []
        self.display_var = tk.StringVar(value="0")
        self.preview_var = tk.StringVar(value="")

        self._build_interface()
        self._center_on_screen()
        self._bind_keyboard()
        self.root.bind("<Control-c>", lambda e: self.copy._copy_answer())


    def _build_interface(self):
        container = tk.Frame(self.root, padx=8, pady=8)
        container.pack()

        total_cols = len(KEYPAD_GRID[0])

        preview = tk.Label(
            container,
            textvariable=self.preview_var,
            font=(UI_FONT, PREVIEW_TEXT_SIZE),
            anchor="e",
            padx=6
        )
        preview.grid(row=0, column=0, columnspan=total_cols, sticky="we")


        screen = tk.Label(
            container,
            textvariable=self.display_var,
            font=(UI_FONT, SCREEN_TEXT_SIZE),
            anchor="e",
            padx=6
        )
        screen.grid(row=1, column=0, columnspan=total_cols, sticky="we", pady=(0, 8))

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
                btn.grid(row=r_idx + 2, column=c_idx, padx=2, pady=2)

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
            self.display_var.set("")

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



        elif key == "MC":
            self.memory = 0.0
        elif key == "MR":
            self.display_var.set(self._clean_output(self.memory))
            self.reset_next = True
        elif key == "M+":
            self.memory += float(current)
            self.reset_next = True
        elif key == "M-":
            self.memory -= float(current)
            self.reset_next = True
        
        elif key == "x²":
            val = float(current) ** 2
            self.display_var.set(self._clean_output(val))
            self.reset_next = True
        elif key == "√":
            val = float(current)
            self.display_var.set("Error" if val < 0 else self._clean_output(math.sqrt(val)))
            self.reset_next = True
        elif key == "1/x":
            val = float(current)
            self.display_var.set("Error" if val == 0 else self._clean_output(1 / val))
            self.reset_next = True
        elif key == "HIST":
            self._open_history()

        elif key in OPERATIONS:
            if self.first_val is not None and self.active_op is not None and not self.reset_next:
                second_val = float(current)
                answer = OPERATIONS[self.active_op](self.first_val, second_val)
                clean_ans = self._clean_output(answer)
                self.display_var.set(clean_ans)
                if clean_ans == "Error":
                    self.first_val = None
                    self.active_op = None
                    self.preview_var.set("")
                    return
                self.first_val = float(clean_ans)
            else:
                self.first_val = float(current)
            self.active_op = key
            self.reset_next = True
            self.preview_var.set(f"{self._clean_output(self.first_val)} {key}")

        elif key == "=":
            if self.first_val is not None and self.active_op is not None:
                second_val = float(current)
                math_func = OPERATIONS[self.active_op]
                answer = math_func(self.first_val, second_val)
                clean_ans = self._clean_output(answer)

                equation = f"{self._clean_output(self.first_val)} {self.active_op} {self._clean_output(second_val)} = {clean_ans}"
                self.preview_var.set(equation)
                self.display_var.set(clean_ans)

                if clean_ans != "Error":
                    self.history.append(equation)  # <-- Save to history list

                self.first_val = None
                self.active_op = None
                self.reset_next = True


    def _bind_keyboard(self):
        key_map = {
            "*": "×",
            "/": "÷",
            "\r": "=",
            "\x08": BACKSPACE,
            "\x1b": "C"
        }
        def on_type(event):
            char = event.char
            if char.isdigit() or char in "+-.%^":
                self._on_key_press(char)
            elif char in key_map:
                self._on_key_press(key_map[char])
        self.root.bind("<Key>", on_type)

    def _copy_answer(self):
        self.root.clipboard_clear()
        self.root.clipboard_append(self.display_var.get())
        self.preview_var.set("Copied!")

    def _open_history(self):
        popup = tk.Toplevel(self.root)
        popup.title("History")
        popup.resizable(False, False)
        
        listbox = tk.Listbox(popup, font=(UI_FONT, 14), width=28, height=10)
        listbox.pack(padx=10, pady=10)
        for item in reversed(self.history):
            listbox.insert(tk.END, item)
        
        def use_selected(event):
            if listbox.curselection():
                chosen = listbox.get(listbox.curselection())
                result_only = chosen.split("=")[-1].strip()
                self.display_var.set(result_only)
                self.reset_next = True
                popup.destroy()
        listbox.bind("<Double-Button-1>", use_selected)

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
