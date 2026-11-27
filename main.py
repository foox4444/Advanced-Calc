import tkinter as tk
import operator as op
import math
import ast

# Variables
UI_FONT = "Helvetica"
SCREEN_TEXT_SIZE = 40
KEY_TEXT_SIZE = 18
PREVIEW_TEXT_SIZE = 14

#Theme stuff
def rgb(r, g, b):
    return f"#{r:02x}{g:02x}{b:02x}"

THEMES = {
    "dark": {
        "bg": rgb(30, 30, 30),
        "screen_fg": rgb(255, 255, 255),
        "preview_fg": rgb(160, 160, 160),
        "num_bg": rgb(45, 45, 45),
        "op_bg": rgb(255, 159, 10),
        "func_bg": rgb(58, 58, 60),
        "btn_fg": rgb(255, 255, 255),
        "op_fg": rgb(255, 255, 255)
    },
    "light": {
        "bg": rgb(243, 243, 243),
        "screen_fg": rgb(0, 0, 0),
        "preview_fg": rgb(85, 85, 85),
        "num_bg": rgb(255, 255, 255),
        "op_bg": rgb(255, 159, 10),
        "func_bg": rgb(224, 224, 224),
        "btn_fg": rgb(0, 0, 0),
        "op_fg": rgb(255, 255, 255)
    }
}

BACKSPACE = "DEL"

KEYPAD_GRID = [
    ["MC", "MR", "M+", "M-"],
    ["(", ")", "^", "THM"],
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

        self.reset_next = False
        self.memory = 0.0
        self.history = []
        self.display_var = tk.StringVar(value="0")
        self.preview_var = tk.StringVar(value="")
        self.memory_var = tk.StringVar(value="")
        self.theme = "light"
        self.buttons = []

        self._build_interface()
        self._center_on_screen()
        self._bind_keyboard()
        self.root.bind("<Control-c>", lambda e: self._copy_answer())
        self.root.bind("<Control-v>", lambda e: self._paste_number())
        self._toggle_theme()


    def _build_interface(self):
        self.container = tk.Frame(self.root, padx=8, pady=8)
        self.container.pack()

        total_cols = len(KEYPAD_GRID[0])

        self.mem_label = tk.Label(
            self.container,
            textvariable=self.memory_var,
            font=(UI_FONT, 12, "bold"),
            anchor="w",
            padx=6
        )
        self.mem_label.grid(row=0, column=0, sticky="w")

        self.preview = tk.Label(
            self.container,
            textvariable=self.preview_var,
            font=(UI_FONT, PREVIEW_TEXT_SIZE),
            anchor="e",
            padx=6
        )
        self.preview.grid(row=0, column=1, columnspan=total_cols - 1, sticky="we")

        self.screen = tk.Label(
            self.container,
            textvariable=self.display_var,
            font=(UI_FONT, SCREEN_TEXT_SIZE),
            anchor="e",
            padx=6
        )
        self.screen.grid(row=1, column=0, columnspan=total_cols, sticky="we", pady=(0, 8))

        for r_idx, row_items in enumerate(KEYPAD_GRID):
            for c_idx, key_text in enumerate(row_items):
                btn = tk.Button(
                    self.container,
                    text=key_text,
                    font=(UI_FONT, KEY_TEXT_SIZE),
                    width=4,
                    height=1,
                    command=lambda k=key_text: self._on_key_press(k)
                )
                btn.grid(row=r_idx + 2, column=c_idx, padx=2, pady=2)
                self.buttons.append((btn, key_text))

    def _clean_output(self, number):
        if isinstance(number, str):
            return number
        rounded = round(number, 10)
        return str(int(rounded)) if rounded.is_integer() else str(rounded)

    def _on_key_press(self, key):
        current = self.display_var.get() or "0"

        if current == "Error":
            if key == "C":
                self.display_var.set("0")
                self.preview_var.set("")
                return
            elif key.isdigit():
                self.display_var.set(key)
                self.preview_var.set("")
                return
            else:
                return

        if key == "C":
            self.reset_next = False
            self.display_var.set("0")
            self.preview_var.set("")

        elif key == BACKSPACE:
            if len(current) > 1 and not (len(current) == 2 and current.startswith("-")):
                self.display_var.set(current[:-1])
            else:
                self.display_var.set("0")

        elif key == "±":
            if current != "0":
                try:
                    val = float(current) * -1
                    self.display_var.set(self._clean_output(val))
                except ValueError:
                    self.preview_var.set("Finish equation first")

        elif key == "%":
            try:
                val = float(current) / 100
                self.display_var.set(self._clean_output(val))
            except ValueError:
                self.preview_var.set("Finish equation first")

        elif key == ".":
            if self.reset_next:
                self.display_var.set("0.")
                self.reset_next = False
            else: 
                last_num = current
                for op_char in ["+", "-", "×", "÷", "^", "(", ")"]:
                    last_num = last_num.split(op_char)[-1]
                if "." not in last_num:
                    self.display_var.set(current + ".")

        elif key.isdigit() or key in {"(", ")"}:
            if current == "0" or self.reset_next:
                self.display_var.set(key)
                self.reset_next = False
            else:
                self.display_var.set(current + key)



        elif key == "MC":
            self.memory = 0.0
            self.memory_var.set("")
        elif key == "MR":
            self.display_var.set(self._clean_output(self.memory))
            self.reset_next = True
        elif key == "M+":
            try:
                self.memory += float(current)
                self.memory_var.set("M" if self.memory != 0 else "")
                self.reset_next = True
            except ValueError:
                self.preview_var.set("Press = first")
        elif key == "M-":
            try:
                self.memory -= float(current)
                self.memory_var.set("M" if self.memory != 0 else "")
                self.reset_next = True
            except ValueError:
                self.preview_var.set("Press = first")
        
        elif key == "x²":
            try:
                val = float(current) ** 2
                self.display_var.set(self._clean_output(val))
                self.reset_next = True
            except ValueError:
                self.preview_var.set("Press = first")
        elif key == "√":
            try:
                val = float(current)
                self.display_var.set("Error" if val < 0 else self._clean_output(math.sqrt(val)))
                self.reset_next = True
            except ValueError:
                self.preview_var.set("Press = first")
        elif key == "1/x":
            try:
                val = float(current)
                self.display_var.set("Error" if val == 0 else self._clean_output(1 / val))
                self.reset_next = True
            except ValueError:
                self.preview_var.set("Press = first")
        elif key == "HIST":
            self._open_history()
        elif key == "THM":
            self._toggle_theme()

        elif key in OPERATIONS:
            self.reset_next = False
            if current[-1] in OPERATIONS:
                self.display_var.set(current[:-1] + key)
            else:
                self.display_var.set(current + key)

        elif key == "=":
            try:
                answer = self._safe_eval(current)
                clean_ans = self._clean_output(answer)
                equation = f"{current} = {clean_ans}"
                self.preview_var.set(equation)
                self.display_var.set(clean_ans)
                self.history.append(equation)
                self.reset_next = True
            except ZeroDivisionError:
                self.display_var.set("Error")
                self.reset_next = True
            except Exception:
                self.preview_var.set("Syntax Error")

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
            if char.isdigit() or char in "+-.%^()":
                self._on_key_press(char)
            elif char in key_map:
                self._on_key_press(key_map[char])
        self.root.bind("<Key>", on_type)

    def _copy_answer(self):
        self.root.clipboard_clear()
        self.root.clipboard_append(self.display_var.get())
        self.preview_var.set("Copied!")

    def _paste_number(self):
        try:
            text = self.root.clipboard_get().strip()
            val = float(text)
            self.display_var.set(self._clean_output(val))
            self.reset_next = False
        except (tk.TclError, ValueError):
            self.preview_var.set("Invalid paste")

    def _toggle_theme(self):
        self.theme = "light" if self.theme == "dark" else "dark"
        t = THEMES[self.theme]

        self.root.configure(bg=t["bg"])
        self.container.configure(bg=t["bg"])
        self.screen.configure(bg=t["bg"], fg=t["screen_fg"], bd=0, highlightthickness=0)
        self.preview.configure(bg=t["bg"], fg=t["preview_fg"], bd=0, highlightthickness=0)
        self.mem_label.configure(bg=t["bg"], fg=t["op_bg"], bd=0, highlightthickness=0)
        
        for btn, key in self.buttons:
            if key in {"+", "-", "×", "÷", "="}:
                btn.configure(bg=t["op_bg"], fg=t["op_fg"], relief="flat")
            elif key.isdigit() or key == ".":
                btn.configure(bg=t["num_bg"], fg=t["btn_fg"], relief="flat")
            else:
                btn.configure(bg=t["func_bg"], fg=t["btn_fg"], relief="flat")

    def _safe_eval(self, expr):
        clean_expr = expr.replace("×", "*").replace("÷", "/").replace("^", "**")
        allowed_ops = {
            ast.Add: op.add, ast.Sub: op.sub,
            ast.Mult: op.mul, ast.Div: op.truediv,
            ast.Pow: op.pow, ast.USub: op.neg
        }
        
        def _eval_node(node):
            if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
                return node.value
            elif isinstance(node, ast.BinOp) and type(node.op) in allowed_ops:
                left = _eval_node(node.left)
                right = _eval_node(node.right)
                if isinstance(node.op, ast.Div) and right == 0:
                    raise ZeroDivisionError
                return allowed_ops[type(node.op)](left, right)
            elif isinstance(node, ast.UnaryOp) and type(node.op) in allowed_ops:
                return allowed_ops[type(node.op)](_eval_node(node.operated))
            raise ValueError("Unsupported syntax")
        tree = ast.parse(clean_expr, mode="eval")
        return _eval_node(tree.body)

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
