import requests

API_KEY = "e21904491c42219d9ca6db66d5e9964e"
URL = "https://api.openweathermap.org/data/2.5/weather"


def build_params(user_input):
    """Decide whether the user typed a city or a ZIP/PIN code."""
    if user_input.isdigit():
        country = input("Country code for this ZIP/PIN (e.g. IN, US) [IN]: ").strip() or "IN"
        return {"zip": f"{user_input},{country}", "appid": API_KEY, "units": "metric"}
    return {"q": user_input, "appid": API_KEY, "units": "metric"}


def get_weather(user_input):
    """Call the API. Returns the data (a dict) or None if something went wrong."""
    try:
        response = requests.get(URL, params=build_params(user_input), timeout=10)
    except requests.exceptions.Timeout:
        print("The request timed out. Try again.")
        return None
    except requests.exceptions.ConnectionError:
        print("No internet connection.")
        return None

    if response.status_code == 401:
        print("Invalid API key. New keys can take up to 2 hours to activate.")
        return None
    if response.status_code == 404:
        print("City / ZIP not found. Check the spelling.")
        return None
    if response.status_code != 200:
        print(f"Something went wrong (error code {response.status_code}).")
        return None

    return response.json()


def get_advice(temp_c, condition):
    """The 'innovative' bit: a tip based on the weather."""
    condition = condition.lower()
    tips = []
    if "rain" in condition or "drizzle" in condition or "thunder" in condition:
        tips.append("Take an umbrella.")
    if "snow" in condition:
        tips.append("Wear boots, it's snowy.")
    if temp_c >= 35:
        tips.append("Very hot! Drink lots of water and avoid midday sun.")
    elif temp_c >= 25:
        tips.append("Warm. Light cotton clothes are best.")
    elif temp_c >= 15:
        tips.append("Pleasant. A light jacket is enough.")
    else:
        tips.append("Cold. Wear a sweater or coat.")
    return " ".join(tips)


def show_weather(data):
    city = data["name"]
    country = data["sys"]["country"]
    temp_c = data["main"]["temp"]
    temp_f = temp_c * 9 / 5 + 32
    feels_c = data["main"]["feels_like"]
    humidity = data["main"]["humidity"]
    description = data["weather"][0]["description"].title()
    wind_ms = data["wind"]["speed"]
    wind_kmh = wind_ms * 3.6

    print("\n" + "=" * 40)
    print(f"  Weather in {city}, {country}")
    print("=" * 40)
    print(f"  Condition   : {description}")
    print(f"  Temperature : {temp_c:.1f} °C  /  {temp_f:.1f} °F")
    print(f"  Feels like  : {feels_c:.1f} °C")
    print(f"  Humidity    : {humidity}%")
    print(f"  Wind speed  : {wind_ms} m/s ({wind_kmh:.1f} km/h)")
    print("-" * 40)
    print(f"  Tip: {get_advice(temp_c, description)}")
    print("-" * 40 + "\n")


def main():
    print("Weather App (type 'quit' to exit)")
    while True:
        user_input = input("Enter a city name or ZIP code: ").strip()

        if user_input.lower() == "quit":
            print("Goodbye!")
            break
        if user_input == "":
            print("Please enter something, the input cannot be empty.")
            continue

        data = get_weather(user_input)
        if data is not None:
            show_weather(data)


main()
