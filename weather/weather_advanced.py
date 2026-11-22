import tkinter as tk
from io import BytesIO
from datetime import datetime, timezone, timedelta

import requests
from PIL import Image, ImageTk

API_KEY = "e21904491c42219d9ca6db66d5e9964e"
BASE = "https://api.openweathermap.org/data/2.5"
ICON_URL = "https://openweathermap.org/img/wn/{}@2x.png"

# ---------- Colours (sky-blue theme) ----------
SKY = "#CFE8FF"          # window background
WHITE = "#FFFFFF"
BLUE = "#2563EB"         # main button colour
BLUE_HOVER = "#1D4ED8"   # button when mouse is over it
BLUE_PRESS = "#1E40AF"   # button while being clicked
LIGHT = "#EAF4FF"        # small cards
LIGHT_HOVER = "#D3E8FF"  # small cards on hover
BORDER = "#B9D8F5"
TEXT = "#0F2A4A"
MUTED = "#5B7A9D"
ERROR = "#B91C1C"
FONT = "Helvetica Neue"
PLACEHOLDER = "Search city or ZIP code..."


class WeatherError(Exception):
    """Our own error type, carrying a friendly message."""


def api_get(endpoint, query):
    if query.isdigit():
        params = {"zip": f"{query},IN"}  # change IN to your country code if needed
    else:
        params = {"q": query}
    params.update({"appid": API_KEY, "units": "metric"})

    try:
        r = requests.get(f"{BASE}/{endpoint}", params=params, timeout=10)
    except requests.exceptions.Timeout:
        raise WeatherError("Request timed out. Try again.")
    except requests.exceptions.ConnectionError:
        raise WeatherError("No internet connection.")

    if r.status_code == 401:
        raise WeatherError("Invalid API key (new keys can take ~2 hours to activate).")
    if r.status_code == 404:
        raise WeatherError("City not found. Check the spelling.")
    if r.status_code != 200:
        raise WeatherError(f"Server error ({r.status_code}).")
    return r.json()


def local_time(timestamp, tz_offset):
    """Convert a UTC timestamp to the city's local time."""
    return datetime.fromtimestamp(timestamp, tz=timezone.utc) + timedelta(seconds=tz_offset)


def get_advice(temp_c, condition):
    tips = []
    if condition in ("Rain", "Drizzle", "Thunderstorm"):
        tips.append("Take an umbrella.")
    if condition == "Snow":
        tips.append("Wear boots.")
    if temp_c >= 35:
        tips.append("Very hot, stay hydrated!")
    elif temp_c >= 25:
        tips.append("Warm, wear light clothes.")
    elif temp_c >= 15:
        tips.append("Pleasant, a light jacket is fine.")
    else:
        tips.append("Cold, wear a coat.")
    return " ".join(tips)


# ---------- Custom widgets ----------
class HoverButton(tk.Label):
    """
    A button made from a Label. (On Mac, the normal tk.Button ignores
    colours, so we build our own. This also lets us add hover effects.)
    """

    def __init__(self, parent, text, command, primary=True):
        super().__init__(parent, text=text, font=(FONT, 12, "bold"),
                         padx=16, pady=9, cursor="pointinghand")
        self.command = command
        self.restyle(primary)
        self.bind("<Enter>", lambda e: self.config(bg=self.hover_bg))
        self.bind("<Leave>", lambda e: self.config(bg=self.normal_bg))
        self.bind("<ButtonPress-1>", lambda e: self.config(bg=self.press_bg))
        self.bind("<ButtonRelease-1>", self.on_release)

    def restyle(self, primary):
        """primary=True -> blue button with white text. False -> white with blue text."""
        if primary:
            self.normal_bg, self.hover_bg, self.press_bg = BLUE, BLUE_HOVER, BLUE_PRESS
            self.config(fg=WHITE, highlightthickness=1, highlightbackground=BLUE)
        else:
            self.normal_bg, self.hover_bg, self.press_bg = WHITE, LIGHT_HOVER, BORDER
            self.config(fg=BLUE, highlightthickness=1, highlightbackground=BLUE)
        self.config(bg=self.normal_bg)

    def on_release(self, event):
        self.config(bg=self.hover_bg)
        # run the command only if the mouse is still on the button
        if 0 <= event.x <= self.winfo_width() and 0 <= event.y <= self.winfo_height():
            self.command()


def add_hover(frame, normal=LIGHT, hover=LIGHT_HOVER):
    """Make a frame (and the labels inside it) change colour on mouse-over."""
    widgets = [frame] + frame.winfo_children()

    def set_bg(color):
        for w in widgets:
            w.config(bg=color)

    def on_leave(event):
        under_mouse = frame.winfo_containing(event.x_root, event.y_root)
        if under_mouse in widgets:
            return  # mouse just moved onto a label inside the card
        set_bg(normal)

    for w in widgets:
        w.bind("<Enter>", lambda e: set_bg(hover))
        w.bind("<Leave>", on_leave)


def make_card(parent):
    """A white panel with a soft blue border."""
    return tk.Frame(parent, bg=WHITE, highlightthickness=1, highlightbackground=BORDER)


class WeatherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Weather")
        self.root.geometry("720x800")
        self.root.configure(bg=SKY)
        self.use_f = False
        self.current = None
        self.forecast = None
        self.icon_cache = {}
        self.placeholder_on = False

        self.build_header()
        self.build_search_bar()
        self.build_main_card()
        self.build_forecast_cards()
        self.show_placeholder()
        self.root.focus()

    # ---------- building the screen ----------
    def build_header(self):
        tk.Label(self.root, text="☁️  Weather", bg=SKY, fg=TEXT,
                 font=(FONT, 28, "bold")).pack(pady=(18, 0))
        tk.Label(self.root, text="Real-time conditions & forecast", bg=SKY, fg=MUTED,
                 font=(FONT, 12)).pack()

    def build_search_bar(self):
        row = tk.Frame(self.root, bg=SKY)
        row.pack(pady=(14, 4), padx=20, fill="x")

        # the white search box (a frame holding an icon + an entry)
        self.search_box = tk.Frame(row, bg=WHITE, highlightthickness=2, highlightbackground=BORDER)
        self.search_box.pack(side="left", fill="x", expand=True)
        tk.Label(self.search_box, text="🔍", bg=WHITE, font=(FONT, 14)).pack(side="left", padx=(10, 0))
        self.entry = tk.Entry(self.search_box, font=(FONT, 14), bd=0, relief="flat",
                              highlightthickness=0, bg=WHITE, fg=TEXT, insertbackground=TEXT)
        self.entry.pack(side="left", fill="x", expand=True, padx=8, ipady=8)
        self.entry.bind("<FocusIn>", self.on_focus_in)
        self.entry.bind("<FocusOut>", self.on_focus_out)
        self.entry.bind("<Return>", lambda e: self.get_weather())

        HoverButton(row, "Get Weather", self.get_weather, primary=True).pack(side="left", padx=(10, 0))
        HoverButton(row, "📍 Detect", self.detect_location, primary=False).pack(side="left", padx=(8, 0))

        # error / status message (shown inside the window)
        self.status_label = tk.Label(self.root, text="", bg=SKY, fg=ERROR, font=(FONT, 12, "bold"))
        self.status_label.pack(pady=(2, 0))

    def build_main_card(self):
        card = make_card(self.root)
        card.pack(padx=20, pady=(6, 8), fill="x")
        inner = tk.Frame(card, bg=WHITE)
        inner.pack(padx=20, pady=14, fill="x")

        # top row: city + date on the left, C/F switch on the right
        top = tk.Frame(inner, bg=WHITE)
        top.pack(fill="x")
        left = tk.Frame(top, bg=WHITE)
        left.pack(side="left")
        self.city_label = tk.Label(left, bg=WHITE, fg=TEXT, font=(FONT, 20, "bold"))
        self.city_label.pack(anchor="w")
        self.date_label = tk.Label(left, bg=WHITE, fg=MUTED, font=(FONT, 11))
        self.date_label.pack(anchor="w")

        switch = tk.Frame(top, bg=WHITE)
        switch.pack(side="right")
        self.c_btn = HoverButton(switch, "°C", lambda: self.set_unit(False), primary=True)
        self.f_btn = HoverButton(switch, "°F", lambda: self.set_unit(True), primary=False)
        self.c_btn.config(padx=12, pady=5)
        self.f_btn.config(padx=12, pady=5)
        self.c_btn.pack(side="left")
        self.f_btn.pack(side="left")

        # middle row: icon, big temperature, description
        mid = tk.Frame(inner, bg=WHITE)
        mid.pack(pady=(6, 6))
        self.icon_label = tk.Label(mid, bg=WHITE)
        self.icon_label.grid(row=0, column=0, rowspan=2)
        self.temp_label = tk.Label(mid, bg=WHITE, fg=BLUE, font=(FONT, 52, "bold"))
        self.temp_label.grid(row=0, column=1, padx=(6, 0))
        self.desc_label = tk.Label(mid, bg=WHITE, fg=TEXT, font=(FONT, 14))
        self.desc_label.grid(row=1, column=1)

        # three small info chips
        chips = tk.Frame(inner, bg=WHITE)
        chips.pack(fill="x")
        self.chip_values = {}
        for i, name in enumerate(["Feels like", "Humidity", "Wind"]):
            chip = tk.Frame(chips, bg=LIGHT, padx=8, pady=8)
            chip.grid(row=0, column=i, padx=4, sticky="nsew")
            chips.grid_columnconfigure(i, weight=1, uniform="chips")
            tk.Label(chip, text=name, bg=LIGHT, fg=MUTED, font=(FONT, 11)).pack()
            value = tk.Label(chip, text="--", bg=LIGHT, fg=TEXT, font=(FONT, 15, "bold"))
            value.pack()
            self.chip_values[name] = value
            add_hover(chip)

        self.advice_label = tk.Label(inner, bg=WHITE, fg=BLUE_HOVER, font=(FONT, 12, "italic"),
                                     wraplength=600)
        self.advice_label.pack(pady=(10, 0))

        # what to show before the first search
        self.city_label.config(text="Welcome 👋")
        self.date_label.config(text="Search for a city to see the weather")
        self.temp_label.config(text="--")

    def build_forecast_cards(self):
        hourly_card = make_card(self.root)
        hourly_card.pack(padx=20, pady=4, fill="x")
        tk.Label(hourly_card, text="Hourly forecast (3-hour steps)", bg=WHITE, fg=TEXT,
                 font=(FONT, 13, "bold")).pack(anchor="w", padx=16, pady=(10, 4))
        self.hourly_frame = tk.Frame(hourly_card, bg=WHITE)
        self.hourly_frame.pack(padx=12, pady=(0, 12), fill="x")

        daily_card = make_card(self.root)
        daily_card.pack(padx=20, pady=(4, 12), fill="x")
        tk.Label(daily_card, text="5-day forecast", bg=WHITE, fg=TEXT,
                 font=(FONT, 13, "bold")).pack(anchor="w", padx=16, pady=(10, 4))
        self.daily_frame = tk.Frame(daily_card, bg=WHITE)
        self.daily_frame.pack(padx=12, pady=(0, 12), fill="x")

    # ---------- search box behaviour ----------
    def show_placeholder(self):
        self.entry.delete(0, tk.END)
        self.entry.insert(0, PLACEHOLDER)
        self.entry.config(fg=MUTED)
        self.placeholder_on = True

    def on_focus_in(self, event):
        self.search_box.config(highlightbackground=BLUE)  # blue glow when clicked
        if self.placeholder_on:
            self.entry.delete(0, tk.END)
            self.entry.config(fg=TEXT)
            self.placeholder_on = False

    def on_focus_out(self, event):
        self.search_box.config(highlightbackground=BORDER)
        if self.entry.get().strip() == "":
            self.show_placeholder()

    def get_query(self):
        return "" if self.placeholder_on else self.entry.get().strip()

    # ---------- helpers ----------
    def fmt_temp(self, celsius):
        if self.use_f:
            return f"{celsius * 9 / 5 + 32:.0f}°F"
        return f"{celsius:.0f}°C"

    def get_icon(self, code, size=None):
        key = (code, size)
        if key not in self.icon_cache:
            try:
                data = requests.get(ICON_URL.format(code), timeout=10).content
                img = Image.open(BytesIO(data))
                if size:
                    img = img.resize((size, size))
                self.icon_cache[key] = ImageTk.PhotoImage(img)
            except Exception:
                return None
        return self.icon_cache[key]

    def show_status(self, message, is_error=True):
        self.status_label.config(text=message, fg=ERROR if is_error else BLUE)

    # ---------- actions ----------
    def get_weather(self, query=None):
        query = query or self.get_query()
        if query == "":
            self.show_status("Please enter a city name or ZIP code.")
            return
        self.show_status("Fetching weather...", is_error=False)
        self.root.update_idletasks()  # show the message before the slow network call
        try:
            self.current = api_get("weather", query)
            self.forecast = api_get("forecast", query)
        except WeatherError as e:
            self.show_status(str(e))
            return
        self.show_status("")
        self.render()

    def detect_location(self):
        self.show_status("Detecting your location...", is_error=False)
        self.root.update_idletasks()
        try:
            city = requests.get("https://ipinfo.io/json", timeout=10).json()["city"]
        except Exception:
            self.show_status("Could not detect your location.")
            return
        self.on_focus_in(None)
        self.entry.delete(0, tk.END)
        self.entry.insert(0, city)
        self.get_weather(city)

    def set_unit(self, use_f):
        self.use_f = use_f
        self.c_btn.restyle(primary=not use_f)
        self.f_btn.restyle(primary=use_f)
        if self.current:
            self.render()

    # ---------- drawing the data ----------
    def render(self):
        c = self.current
        main = c["weather"][0]["main"]
        tz = c["timezone"]

        self.city_label.config(text=f"{c['name']}, {c['sys']['country']}")
        self.date_label.config(text=local_time(c["dt"], tz).strftime("%A, %d %B  •  %I:%M %p"))
        self.temp_label.config(text=self.fmt_temp(c["main"]["temp"]))
        self.desc_label.config(text=c["weather"][0]["description"].title())

        icon = self.get_icon(c["weather"][0]["icon"])
        self.icon_label.config(image=icon)
        self.icon_label.image = icon  # keep a reference or tkinter deletes the image!

        self.chip_values["Feels like"].config(text=self.fmt_temp(c["main"]["feels_like"]))
        self.chip_values["Humidity"].config(text=f"{c['main']['humidity']}%")
        self.chip_values["Wind"].config(text=f"{c['wind']['speed'] * 3.6:.0f} km/h")
        self.advice_label.config(text="Tip: " + get_advice(c["main"]["temp"], main))

        self.render_hourly()
        self.render_daily()

    def clear(self, frame):
        for child in frame.winfo_children():
            child.destroy()

    def make_mini_card(self, parent, column, title, icon_code, text):
        card = tk.Frame(parent, bg=LIGHT, padx=6, pady=8)
        card.grid(row=0, column=column, padx=4, sticky="nsew")
        parent.grid_columnconfigure(column, weight=1, uniform="mini")
        tk.Label(card, text=title, bg=LIGHT, fg=MUTED, font=(FONT, 11, "bold")).pack()
        icon = self.get_icon(icon_code, size=50)
        icon_lbl = tk.Label(card, image=icon, bg=LIGHT)
        icon_lbl.image = icon
        icon_lbl.pack()
        tk.Label(card, text=text, bg=LIGHT, fg=TEXT, font=(FONT, 12, "bold")).pack()
        add_hover(card)

    def render_hourly(self):
        self.clear(self.hourly_frame)
        tz = self.forecast["city"]["timezone"]
        for i, item in enumerate(self.forecast["list"][:6]):
            t = local_time(item["dt"], tz).strftime("%I %p").lstrip("0")
            self.make_mini_card(self.hourly_frame, i, t, item["weather"][0]["icon"],
                                self.fmt_temp(item["main"]["temp"]))

    def render_daily(self):
        self.clear(self.daily_frame)
        tz = self.forecast["city"]["timezone"]
        days = {}  # date -> list of forecast entries for that day
        for item in self.forecast["list"]:
            date = local_time(item["dt"], tz).date()
            days.setdefault(date, []).append(item)

        for i, (date, items) in enumerate(list(days.items())[:5]):
            low = min(x["main"]["temp_min"] for x in items)
            high = max(x["main"]["temp_max"] for x in items)
            # use the entry closest to midday for the day's icon
            noon = min(items, key=lambda x: abs(local_time(x["dt"], tz).hour - 12))
            self.make_mini_card(self.daily_frame, i, date.strftime("%a"),
                                noon["weather"][0]["icon"],
                                f"{self.fmt_temp(high)} / {self.fmt_temp(low)}")


root = tk.Tk()
app = WeatherApp(root)
root.mainloop()
