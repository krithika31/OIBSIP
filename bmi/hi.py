import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
import math

# ---------------------------------------------------------
# BMI CALCULATOR - upgraded version
# Built with CustomTkinter
# ---------------------------------------------------------

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

# Colour palette - keeps the original cream and teal look
BG = "#EAF4F4"
CARD = "#FFFFFF"
TEAL = "#245B65"
TEAL_HOVER = "#397C85"
MUTED = "#526D72"
BORDER = "#B8D3D0"
PALE = "#F7FBFA"
GREEN = "#16865A"
AMBER = "#D58A35"
RED = "#D65B5B"
FONT = "Avenir Next"

root = ctk.CTk()
root.title("BMI Calculator")
root.geometry("560x900")
root.minsize(500, 700)
root.configure(fg_color=BG)

# Store completed calculations for this session
bmi_history = []
last_bmi = None


# ------------------------- Helpers -------------------------

def make_card(parent, **kwargs):
    return ctk.CTkFrame(
        parent,
        corner_radius=22,
        fg_color=CARD,
        **kwargs
    )


def show_error(title, message):
    messagebox.showerror(title, message, parent=root)


def get_weight_kg():
    """Read the weight field and return kilograms."""
    try:
        value = float(weight_entry.get().strip())
    except ValueError:
        raise ValueError("Please enter your weight using numbers only.")

    if value <= 0:
        raise ValueError("Weight must be greater than zero.")

    unit = weight_unit.get()
    return value if unit == "kg" else value * 0.45359237


def get_height_m():
    """Read the selected height format and return metres."""
    unit = height_unit.get()

    if unit == "cm":
        try:
            cm = float(height_cm_entry.get().strip())
        except ValueError:
            raise ValueError("Please enter your height in centimetres.")

        if cm <= 0:
            raise ValueError("Height must be greater than zero.")
        return cm / 100

    try:
        feet = int(feet_entry.get().strip())
        inches_text = inches_entry.get().strip()
        inches = float(inches_text) if inches_text else 0.0
    except ValueError:
        raise ValueError("Enter feet as a whole number and inches as a number.")

    if feet < 0 or inches < 0 or inches >= 12:
        raise ValueError("Enter a valid height. Inches must be from 0 to less than 12.")

    total_inches = feet * 12 + inches
    if total_inches <= 0:
        raise ValueError("Height must be greater than zero.")

    return total_inches * 0.0254


def get_bmi_category(bmi):
    if bmi < 18.5:
        return (
            "Underweight range",
            "Your BMI is a little below the healthy range. "
                "Focus on nourishing your body.",
            AMBER,
            "Focus on balanced, nourishing meals and regular health check-ups."
        )
    elif bmi < 25:
        return (
            "Healthy range",
            "You're in the healthy BMI range! Keep taking "
                "care of yourself and maintaining those healthy habits!",
            GREEN,
            "Continue with balanced meals, enjoyable movement and good sleep."
        )
    elif bmi < 30:
        return (
            "Overweight range",
            "Your BMI is a little above the healthy range. "
                "Let's work towards a healthier you!",
            AMBER,
            "Small, sustainable habits around food, movement and sleep can support wellbeing."
        )
    else:
        return (
            "Obesity range",
            "Your BMI is above the healthy range. "
                "Let's work towards a healthier lifestyle, "
                "one step at a time!",
            RED,
            "Ask a healthcare professional for advice that considers your overall health."
        )


# ------------------------- Unit controls -------------------------

def update_weight_unit(choice):
    weight_unit_label.configure(text=f"Weight ({choice})")
    weight_entry.delete(0, "end")
    weight_entry.configure(
        placeholder_text="Enter your weight in " + choice
    )


def update_height_unit(choice):
    height_cm_entry.delete(0, "end")
    feet_entry.delete(0, "end")
    inches_entry.delete(0, "end")

    if choice == "cm":
        cm_row.pack(fill="x", padx=22, pady=(0, 16))
        feet_inches_row.pack_forget()
    else:
        cm_row.pack_forget()
        feet_inches_row.pack(fill="x", padx=22, pady=(0, 16))


# ------------------------- BMI gauge -------------------------

def draw_gauge(bmi):
    """Draw a semicircular BMI gauge using a Tkinter Canvas."""
    gauge.delete("all")

    width = 330
    height = 155
    cx = width / 2
    cy = 128
    radius = 105
    line_width = 18

    # Adult BMI scale shown from 10 to 40
    segments = [
        (10, 18.5, "#D9A45F"),
        (18.5, 25, "#69B88B"),
        (25, 30, "#E5BE65"),
        (30, 40, "#D97979"),
    ]

    for low, high, colour in segments:
        start = 180 - ((high - 10) / 30) * 180
        extent = ((high - low) / 30) * 180
        gauge.create_arc(
            cx - radius, cy - radius,
            cx + radius, cy + radius,
            start=start,
            extent=extent,
            style="arc",
            outline=colour,
            width=line_width
        )

    # Keep the needle within the displayed 10-40 scale
    clamped_bmi = max(10, min(40, bmi))
    angle = math.radians(180 - ((clamped_bmi - 10) / 30) * 180)

    needle_length = 82
    nx = cx + needle_length * math.cos(angle)
    ny = cy - needle_length * math.sin(angle)

    gauge.create_line(
        cx, cy, nx, ny,
        fill=TEAL,
        width=4,
        arrow="last",
        arrowshape=(10, 12, 5)
    )
    gauge.create_oval(
        cx - 7, cy - 7, cx + 7, cy + 7,
        fill=TEAL,
        outline=TEAL
    )

    gauge.create_text(
        cx, 145,
        text=f"BMI {bmi:.2f}",
        fill=TEAL,
        font=(FONT, 13, "bold")
    )


# ------------------------- History -------------------------

def add_to_history(bmi, category):
    timestamp = datetime.now().strftime("%d %b %Y, %I:%M %p")
    entry = f"{timestamp}   |   BMI: {bmi:.2f}   |   {category}"
    bmi_history.insert(0, entry)

    history_box.configure(state="normal")
    history_box.delete("1.0", "end")
    history_box.insert("1.0", "\n\n".join(bmi_history))
    history_box.configure(state="disabled")


def clear_history():
    if not bmi_history:
        return

    confirm = messagebox.askyesno(
        "Clear history",
        "Are you sure you want to clear this session's BMI history?",
        parent=root
    )
    if confirm:
        bmi_history.clear()
        history_box.configure(state="normal")
        history_box.delete("1.0", "end")
        history_box.configure(state="disabled")


# ------------------------- Main actions -------------------------

def calculate_bmi():
    global last_bmi

    try:
        weight_kg = get_weight_kg()
        height_m = get_height_m()

        # Basic plausibility check to catch likely typing mistakes
        if height_m < 0.5 or height_m > 2.7:
            raise ValueError("Please check your height. Enter a realistic height.")

        bmi = weight_kg / (height_m * height_m)
        category, caption, colour, recommendation = get_bmi_category(bmi)
        last_bmi = bmi

        result_label.configure(text=f"Your BMI: {bmi:.2f}")
        category_label.configure(text=category, text_color=colour)
        caption_label.configure(text=caption)
        recommendation_label.configure(text=recommendation)
        draw_gauge(bmi)
        add_to_history(bmi, category)

    except ValueError as error:
        show_error("Invalid Input", str(error))


def reset_fields():
    global last_bmi
    weight_entry.delete(0, "end")
    height_cm_entry.delete(0, "end")
    feet_entry.delete(0, "end")
    inches_entry.delete(0, "end")

    result_label.configure(text="Your BMI: --")
    category_label.configure(
        text="Your category will appear here",
        text_color=TEAL
    )
    caption_label.configure(text="Your result will appear here.")
    recommendation_label.configure(
        text="Your recommendation will appear here."
    )
    gauge.delete("all")
    last_bmi = None


# ------------------------- Scrollable application layout -------------------------

main = ctk.CTkScrollableFrame(
    root,
    fg_color="transparent",
    scrollbar_button_color="#B8D5D0",
    scrollbar_button_hover_color="#9BBFB9"
)
main.pack(fill="both", expand=True, padx=12, pady=8)

# Heading
title = ctk.CTkLabel(
    main,
    text="BMI CALCULATOR",
    font=(FONT, 28, "bold"),
    text_color=TEAL
)
title.pack(pady=(18, 4))

welcome = ctk.CTkLabel(
    main,
    text="Heyyy! Let's check your BMI.",
    font=(FONT, 15),
    text_color=MUTED
)
welcome.pack(pady=(0, 18))

# Input card
input_frame = make_card(main)
input_frame.pack(padx=18, fill="x", pady=5)

# Weight heading and unit selector
weight_top = ctk.CTkFrame(input_frame, fg_color="transparent")
weight_top.pack(fill="x", padx=22, pady=(18, 5))

weight_unit_label = ctk.CTkLabel(
    weight_top,
    text="Weight (kg)",
    font=(FONT, 14, "bold"),
    text_color=TEAL
)
weight_unit_label.pack(side="left")

weight_unit = ctk.StringVar(value="kg")
weight_selector = ctk.CTkSegmentedButton(
    weight_top,
    values=["kg", "lb"],
    variable=weight_unit,
    command=update_weight_unit,
    selected_color=TEAL,
    selected_hover_color=TEAL_HOVER,
    font=(FONT, 11)
)
weight_selector.pack(side="right")

weight_entry = ctk.CTkEntry(
    input_frame,
    placeholder_text="Enter your weight in kg",
    height=43,
    corner_radius=12,
    border_width=1,
    border_color=BORDER,
    fg_color=PALE,
    font=(FONT, 14)
)
weight_entry.pack(fill="x", padx=22, pady=(0, 16))

# Height heading and unit selector
height_top = ctk.CTkFrame(input_frame, fg_color="transparent")
height_top.pack(fill="x", padx=22, pady=(0, 5))

height_label = ctk.CTkLabel(
    height_top,
    text="Height",
    font=(FONT, 14, "bold"),
    text_color=TEAL
)
height_label.pack(side="left")

height_unit = ctk.StringVar(value="cm")
height_selector = ctk.CTkSegmentedButton(
    height_top,
    values=["cm", "ft/in"],
    variable=height_unit,
    command=update_height_unit,
    selected_color=TEAL,
    selected_hover_color=TEAL_HOVER,
    font=(FONT, 11)
)
height_selector.pack(side="right")

# Centimetres entry
cm_row = ctk.CTkFrame(input_frame, fg_color="transparent")
cm_row.pack(fill="x", padx=22, pady=(0, 16))

height_cm_entry = ctk.CTkEntry(
    cm_row,
    placeholder_text="Enter your height in cm",
    height=43,
    corner_radius=12,
    border_width=1,
    border_color=BORDER,
    fg_color=PALE,
    font=(FONT, 14)
)
height_cm_entry.pack(fill="x")

# Feet and inches entries
feet_inches_row = ctk.CTkFrame(input_frame, fg_color="transparent")
feet_inches_row.pack_forget()

feet_entry = ctk.CTkEntry(
    feet_inches_row,
    placeholder_text="Feet",
    height=43,
    corner_radius=12,
    border_width=1,
    border_color=BORDER,
    fg_color=PALE,
    font=(FONT, 14)
)
feet_entry.pack(side="left", fill="x", expand=True, padx=(0, 6))

inches_entry = ctk.CTkEntry(
    feet_inches_row,
    placeholder_text="Inches",
    height=43,
    corner_radius=12,
    border_width=1,
    border_color=BORDER,
    fg_color=PALE,
    font=(FONT, 14)
)
inches_entry.pack(side="left", fill="x", expand=True, padx=(6, 0))

# Buttons
button_frame = ctk.CTkFrame(main, fg_color="transparent")
button_frame.pack(pady=15)

calculate_button = ctk.CTkButton(
    button_frame,
    text="Calculate BMI",
    width=175,
    height=44,
    corner_radius=14,
    font=(FONT, 14, "bold"),
    fg_color=TEAL,
    hover_color=TEAL_HOVER,
    command=calculate_bmi
)
calculate_button.pack(side="left", padx=6)

reset_button = ctk.CTkButton(
    button_frame,
    text="Reset",
    width=95,
    height=44,
    corner_radius=14,
    font=(FONT, 14, "bold"),
    fg_color="#B8D5D0",
    hover_color="#9BBFB9",
    text_color=TEAL,
    command=reset_fields
)
reset_button.pack(side="left", padx=6)

# Result card
result_frame = make_card(main)
result_frame.pack(padx=18, fill="x", pady=5)

result_label = ctk.CTkLabel(
    result_frame,
    text="Your BMI: --",
    font=(FONT, 23, "bold"),
    text_color=TEAL
)
result_label.pack(pady=(17, 5))

category_label = ctk.CTkLabel(
    result_frame,
    text="Your category will appear here",
    font=(FONT, 17, "bold"),
    text_color=TEAL
)
category_label.pack(pady=4)

caption_label = ctk.CTkLabel(
    result_frame,
    text="Your result will appear here.",
    font=(FONT, 12),
    text_color=MUTED,
    wraplength=420,
    justify="center"
)
caption_label.pack(padx=20, pady=(4, 8))

# BMI gauge
gauge = ctk.CTkCanvas(
    result_frame,
    width=330,
    height=155,
    bg=CARD,
    highlightthickness=0
)
gauge.pack(pady=(0, 2))

gauge_legend = ctk.CTkLabel(
    result_frame,
    text="Underweight     Healthy     Overweight     Obesity",
    font=(FONT, 9),
    text_color=MUTED
)
gauge_legend.pack(pady=(0, 12))

# Recommendation card
recommendation_frame = make_card(main)
recommendation_frame.pack(padx=18, fill="x", pady=7)

recommendation_title = ctk.CTkLabel(
    recommendation_frame,
    text="A LITTLE HEALTH GUIDANCE",
    font=(FONT, 13, "bold"),
    text_color=TEAL
)
recommendation_title.pack(anchor="w", padx=20, pady=(15, 5))

recommendation_label = ctk.CTkLabel(
    recommendation_frame,
    text="Your recommendation will appear here.",
    font=(FONT, 12),
    text_color=MUTED,
    wraplength=430,
    justify="left"
)
recommendation_label.pack(anchor="w", padx=20, pady=(0, 16))

# History card
history_frame = make_card(main)
history_frame.pack(padx=18, fill="x", pady=7)

history_header = ctk.CTkFrame(history_frame, fg_color="transparent")
history_header.pack(fill="x", padx=18, pady=(14, 5))

history_title = ctk.CTkLabel(
    history_header,
    text="BMI HISTORY",
    font=(FONT, 13, "bold"),
    text_color=TEAL
)
history_title.pack(side="left")

clear_history_button = ctk.CTkButton(
    history_header,
    text="Clear",
    width=65,
    height=28,
    corner_radius=9,
    font=(FONT, 10, "bold"),
    fg_color="#B8D5D0",
    hover_color="#9BBFB9",
    text_color=TEAL,
    command=clear_history
)
clear_history_button.pack(side="right")

history_box = ctk.CTkTextbox(
    history_frame,
    height=100,
    corner_radius=12,
    border_width=1,
    border_color=BORDER,
    fg_color=PALE,
    text_color=MUTED,
    font=(FONT, 11),
    wrap="word"
)
history_box.pack(fill="x", padx=18, pady=(4, 15))
history_box.insert("1.0", "Your BMI calculations will appear here.")
history_box.configure(state="disabled")

# Note and footer
note = ctk.CTkLabel(
    main,
    text=(
        "Note:BMI is only a general screening guide and should be evaluated alongside a physical exam and other health markers by a doctor. "
        
    ),
    font=(FONT, 10),
    text_color=MUTED,
    wraplength=450,
    justify="center"
)
note.pack(padx=20, pady=(12, 5))

footer = ctk.CTkLabel(
    main,
    text="Designed by KRITHIKA A",
    font=(FONT, 11, "italic"),
    text_color=MUTED
)
footer.pack(pady=(8, 25))

# Keyboard shortcut: Enter calculates BMI
root.bind("<Return>", lambda event: calculate_bmi())

root.mainloop()