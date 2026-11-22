
import customtkinter as ctk
from tkinter import messagebox

# Window settings
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

root = ctk.CTk()
root.title("BMI Calculator")
root.geometry("520x760")
root.resizable(False, False)
root.configure(fg_color="#EAF4F4")

# Font style
FONT = "Avenir Next"

# Calculate BMI function
def calculate_bmi():
    try:
        weight = float(weight_entry.get())
        height = float(height_entry.get())

        if weight <= 0 or height <= 0:
            messagebox.showerror(
                "Invalid Input",
                "Please enter positive weight and height!"
            )
            return

        height = height / 100
        bmi = weight / (height * height)

        result_label.configure(
            text=f"Your BMI: {bmi:.2f}"
        )

        if bmi < 18.5:
            category = "Underweight"
            caption = (
                "Your BMI is a little below the healthy range. "
                "Focus on nourishing your body."
            )
            color = "#D58A35"

        elif bmi < 25:
            category = "Normal"
            caption = (
                "You're in the healthy BMI range! Keep taking "
                "care of yourself and maintaining those healthy habits!"
            )
            color = "#16865A"

        elif bmi < 30:
            category = "Overweight"
            caption = (
                "Your BMI is a little above the healthy range. "
                "Let's work towards a healthier you!"
            )
            color = "#D58A35"

        else:
            category = "Obese"
            caption = (
                "Your BMI is above the healthy range. "
                "Let's work towards a healthier lifestyle, "
                "one step at a time!"
            )
            color = "#D65B5B"

        category_label.configure(
            text=category,
            text_color=color
        )

        caption_label.configure(
            text=caption
        )

    except ValueError:
        messagebox.showerror(
            "Invalid Input",
            "Please enter numbers only!"
        )


# Reset function
def reset_fields():
    weight_entry.delete(0, "end")
    height_entry.delete(0, "end")

    result_label.configure(text="Your BMI: --")
    category_label.configure(
        text="Your category will appear here",
        text_color="#245B65"
    )
    caption_label.configure(
        text="Your result will appear here."
    )


# Heading
title = ctk.CTkLabel(
    root,
    text="BMI CALCULATOR",
    font=(FONT, 28, "bold"),
    text_color="#245B65"
)
title.pack(pady=(30, 5))

# Welcome message
welcome = ctk.CTkLabel(
    root,
    text="Heyyy! Let's check your BMI.",
    font=(FONT, 15),
    text_color="#526D72"
)
welcome.pack(pady=(0, 25))


# Input card with rounded corners
input_frame = ctk.CTkFrame(
    root,
    width=420,
    corner_radius=25,
    fg_color="#FFFFFF"
)
input_frame.pack(padx=40, fill="x", pady=5)
input_frame.pack_propagate(False)

# Weight label
weight_label = ctk.CTkLabel(
    input_frame,
    text="Weight (kg)",
    font=(FONT, 14, "bold"),
    text_color="#245B65"
)
weight_label.pack(anchor="w", padx=25, pady=(20, 5))

# Weight input box
weight_entry = ctk.CTkEntry(
    input_frame,
    placeholder_text="Enter your weight",
    height=45,
    corner_radius=12,
    border_width=1,
    border_color="#B8D3D0",
    fg_color="#F7FBFA",
    font=(FONT, 14)
)
weight_entry.pack(fill="x", padx=25)

# Height label
height_label = ctk.CTkLabel(
    input_frame,
    text="Height (cm)",
    font=(FONT, 14, "bold"),
    text_color="#245B65"
)
height_label.pack(anchor="w", padx=25, pady=(20, 5))

# Height input box
height_entry = ctk.CTkEntry(
    input_frame,
    placeholder_text="Enter your height",
    height=45,
    corner_radius=12,
    border_width=1,
    border_color="#B8D3D0",
    fg_color="#F7FBFA",
    font=(FONT, 14)
)
height_entry.pack(fill="x", padx=25, pady=(0, 2))


# Button frame
button_frame = ctk.CTkFrame(
    root,
    fg_color="transparent"
)
button_frame.pack(pady=20)

# Calculate button
calculate_button = ctk.CTkButton(
    button_frame,
    text="Calculate BMI",
    width=180,
    height=45,
    corner_radius=15,
    font=(FONT, 14, "bold"),
    fg_color="#245B65",
    hover_color="#397C85",
    command=calculate_bmi
)
calculate_button.pack(side="left", padx=8)

# Reset button
reset_button = ctk.CTkButton(
    button_frame,
    text="Reset",
    width=100,
    height=45,
    corner_radius=15,
    font=(FONT, 14, "bold"),
    fg_color="#B8D5D0",
    hover_color="#9BBFB9",
    text_color="#245B65",
    command=reset_fields
)
reset_button.pack(side="left", padx=8)


# Result card
result_frame = ctk.CTkFrame(
    root,
    corner_radius=25,
    fg_color="#FFFFFF"
)
result_frame.pack(padx=40, fill="x", pady=5)

# BMI result
result_label = ctk.CTkLabel(
    result_frame,
    text="Your BMI: --",
    font=(FONT, 23, "bold"),
    text_color="#245B65"
)
result_label.pack(pady=(20, 8))

# Category
category_label = ctk.CTkLabel(
    result_frame,
    text="Your category will appear here",
    font=(FONT, 17, "bold"),
    text_color="#245B65"
)
category_label.pack(pady=5)

# Caption
caption_label = ctk.CTkLabel(
    result_frame,
    text="Your result will appear here.",
    font=(FONT, 12),
    text_color="#526D72",
    wraplength=350
)
caption_label.pack(padx=20, pady=(5, 20))


# Footer
footer = ctk.CTkLabel(
    root,
    text="Designed by KRITHIKA A\n",
    font=(FONT, 11, "italic"),
    text_color="#526D72"
)
footer.pack(pady=(100, 50))

# Run application
root.mainloop()
