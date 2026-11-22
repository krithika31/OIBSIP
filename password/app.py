import customtkinter as ctk
import pyperclip

from password_logic import (
    MIN_LENGTH,
    MAX_LENGTH,
    get_character_sets,
    generate_password,
    check_strength,
    add_to_history,
)

# ---------- Colour palette ----------
# ---------- Colour palette: Deep Wine + Dusty Rose ----------
BACKGROUND = "#2A0A16"      # very deep wine (window background)
CARD = "#4A1428"            # deep wine (cards)
TRACK = "#6B2A40"           # lighter wine (slider and bar tracks)
ACCENT = "#D4A5A5"          # dusty rose (buttons, slider, checkboxes)
ACCENT_HOVER = "#C08A93"    # darker dusty rose (hover)
ON_ACCENT = "#3B0A1C"       # dark wine text on top of dusty rose
TEXT = "#F8E9EC"            # soft blush white
MUTED = "#C9A0AB"           # muted rose-grey
SUCCESS_COLOR = "#9FD8B0"
ERROR_COLOR = "#FF8A8A"
STRENGTH_COLORS = {
    "Weak": "#FF7B7B",
    "Medium": "#F4B860",
    "Strong": "#9FD8B0",
}

class PasswordGeneratorApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Secure Password Generator")
        self.geometry("480x800")
        self.minsize(460, 780)
        self.resizable(True, True)
        self.configure(fg_color=BACKGROUND)

        # Variables that remember the checkbox states
        self.upper_var = ctk.BooleanVar(value=False)
        self.lower_var = ctk.BooleanVar(value=False)
        self.numbers_var = ctk.BooleanVar(value=False)
        self.symbols_var = ctk.BooleanVar(value=False)
        self.ambiguous_var = ctk.BooleanVar(value=False)

        # Last 5 passwords (kept in memory only, never saved to a file)
        self.history = []

        self.create_header()
        self.create_result_card()
        self.create_options_card()
        self.create_generate_button()
        self.create_history_card()

    # ---------- Building the screen ----------
    def create_header(self):
        title = ctk.CTkLabel(
            self, text="Password Generator",
            font=ctk.CTkFont(size=28, weight="bold"), text_color=TEXT,
        )
        title.pack(pady=(18, 0))

        subtitle = ctk.CTkLabel(
            self, text="Create strong, random passwords in one click",
            font=ctk.CTkFont(size=13), text_color=MUTED,
        )
        subtitle.pack(pady=(0, 15))

    def create_result_card(self):
        card = ctk.CTkFrame(self, fg_color=CARD, corner_radius=14)
        card.pack(padx=25, pady=10, fill="x")

        self.password_label = ctk.CTkLabel(
            card, text="Click Generate",
            font=ctk.CTkFont(family="Menlo", size=18),
            text_color=TEXT, wraplength=400, height=60,
        )
        self.password_label.pack(padx=15, pady=(15, 5))

        self.strength_bar = ctk.CTkProgressBar(
            card, height=10, progress_color=MUTED
        )
        self.strength_bar.set(0)
        self.strength_bar.pack(padx=20, fill="x")

        self.strength_label = ctk.CTkLabel(
            card, text="Strength: -",
            font=ctk.CTkFont(size=13, weight="bold"), text_color=MUTED,
        )
        self.strength_label.pack(pady=(8, 15))

    def create_options_card(self):
        card = ctk.CTkFrame(self, fg_color=CARD, corner_radius=14)
        card.pack(padx=25, pady=15, fill="x")

        # Length row: the word "Length" on the left, the number on the right
        length_row = ctk.CTkFrame(card, fg_color="transparent")
        length_row.pack(fill="x", padx=20, pady=(15, 0))

        ctk.CTkLabel(
            length_row, text="Length",
            font=ctk.CTkFont(size=15, weight="bold"), text_color=TEXT,
        ).pack(side="left")

        self.length_value_label = ctk.CTkLabel(
            length_row, text="16",
            font=ctk.CTkFont(size=15, weight="bold"), text_color=ACCENT,
        )
        self.length_value_label.pack(side="right")

        self.length_slider = ctk.CTkSlider(
            card, from_=MIN_LENGTH, to=MAX_LENGTH,
            number_of_steps=MAX_LENGTH - MIN_LENGTH,
            command=self.update_length_label,
            progress_color=ACCENT, button_color=ACCENT,
            button_hover_color=ACCENT_HOVER,
        )
        self.length_slider.set(16)
        self.length_slider.pack(fill="x", padx=20, pady=(8, 10))

        # Checkboxes
        self.make_checkbox(card, "Uppercase letters (A-Z)", self.upper_var)
        self.make_checkbox(card, "Lowercase letters (a-z)", self.lower_var)
        self.make_checkbox(card, "Numbers (0-9)", self.numbers_var)
        self.make_checkbox(card, "Symbols (!@#$%)", self.symbols_var)
        self.make_checkbox(
            card, "Exclude look-alike characters (0, O, l, 1, I)",
            self.ambiguous_var, last=True,
        )

    def make_checkbox(self, parent, text, variable, last=False):
        checkbox = ctk.CTkCheckBox(
            parent, text=text, variable=variable,
            checkmark_color=ON_ACCENT,
            fg_color=ACCENT, hover_color=ACCENT_HOVER, text_color=TEXT,
        )
        checkbox.pack(anchor="w", padx=20, pady=(2, 12 if last else 2))

    def create_generate_button(self):
        button = ctk.CTkButton(
            self, text="Generate Password", command=self.on_generate,
            height=44, corner_radius=12,
            fg_color=ACCENT, hover_color=ACCENT_HOVER,
            text_color=ON_ACCENT,
            font=ctk.CTkFont(size=16, weight="bold"),
        )
        button.pack(padx=25, fill="x")

        # Messages (success and errors) appear here, inside the window
        self.message_label = ctk.CTkLabel(
            self, text="", font=ctk.CTkFont(size=13), text_color=MUTED,
        )
        self.message_label.pack(pady=(6, 4))

    def create_history_card(self):
        card = ctk.CTkFrame(self, fg_color=CARD, corner_radius=14)
        card.pack(padx=25, pady=(0, 15), fill="x")

        ctk.CTkLabel(
            card, text="Recent passwords (this session only)",
            font=ctk.CTkFont(size=13, weight="bold"), text_color=MUTED,
        ).pack(anchor="w", padx=20, pady=(10, 2))

        self.history_labels = []
        for index in range(5):
            label = ctk.CTkLabel(
                card, text="-", anchor="w", height=20,
                font=ctk.CTkFont(family="Menlo", size=12), text_color=TEXT,
            )
            # The last row gets extra space below it
            label.pack(fill="x", padx=20, pady=(0, 10 if index == 4 else 0))
            self.history_labels.append(label)

    # ---------- What happens when the user does something ----------
    def update_length_label(self, value):
        self.length_value_label.configure(text=str(int(round(value))))

    def show_message(self, text, color):
        self.message_label.configure(text=text, text_color=color)

    def refresh_history(self):
        for index, label in enumerate(self.history_labels):
            if index < len(self.history):
                label.configure(text=f"{index + 1}.  {self.history[index]}")
            else:
                label.configure(text="-")

    def on_generate(self):
        length = int(round(self.length_slider.get()))

        selected_sets = get_character_sets(
            self.upper_var.get(),
            self.lower_var.get(),
            self.numbers_var.get(),
            self.symbols_var.get(),
            self.ambiguous_var.get(),
        )

        # Try to generate. If the rules are broken, show the error in the window
        try:
            password = generate_password(length, selected_sets)
        except ValueError as error:
            self.show_message(str(error), ERROR_COLOR)
            return

        # Show the password and its strength
        self.password_label.configure(text=password)
        strength_name, fraction = check_strength(password)
        color = STRENGTH_COLORS[strength_name]
        self.strength_bar.set(fraction)
        self.strength_bar.configure(progress_color=color)
        self.strength_label.configure(
            text=f"Strength: {strength_name}", text_color=color
        )

        # Update the history
        add_to_history(self.history, password)
        self.refresh_history()

        # Copy to clipboard automatically
        try:
            pyperclip.copy(password)
            self.show_message(
                "Password generated and copied to clipboard!", SUCCESS_COLOR
            )
        except pyperclip.PyperclipException:
            self.show_message(
                "Password generated, but copying to clipboard failed.",
                ERROR_COLOR,
            )


if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    app = PasswordGeneratorApp()
    app.mainloop()