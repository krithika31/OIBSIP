import random
import secrets
import string

MIN_LENGTH = 8
MAX_LENGTH = 64
MAX_HISTORY = 5
AMBIGUOUS_CHARACTERS = "0Ol1I"


def get_character_sets(use_uppercase, use_lowercase, use_numbers,
                       use_symbols, exclude_ambiguous):
    """Return a list of the selected character sets."""
    selected_sets = []

    if use_uppercase:
        selected_sets.append(string.ascii_uppercase)
    if use_lowercase:
        selected_sets.append(string.ascii_lowercase)
    if use_numbers:
        selected_sets.append(string.digits)
    if use_symbols:
        selected_sets.append(string.punctuation)

    if exclude_ambiguous:
        cleaned_sets = []
        for character_set in selected_sets:
            cleaned = ""
            for character in character_set:
                if character not in AMBIGUOUS_CHARACTERS:
                    cleaned += character
            cleaned_sets.append(cleaned)
        selected_sets = cleaned_sets

    return selected_sets


def generate_password(length, selected_sets):
    """Create a secure password containing every selected character type."""
    if length < MIN_LENGTH or length > MAX_LENGTH:
        raise ValueError(
            f"Length must be between {MIN_LENGTH} and {MAX_LENGTH}."
        )
    if len(selected_sets) < 2:
        raise ValueError("Please select at least 2 character types.")

    password_characters = []

    # One guaranteed character from each selected type
    for character_set in selected_sets:
        password_characters.append(secrets.choice(character_set))

    # Fill the remaining length from all selected characters
    all_characters = "".join(selected_sets)
    while len(password_characters) < length:
        password_characters.append(secrets.choice(all_characters))

    # Shuffle securely so the guaranteed characters are not predictable
    random.SystemRandom().shuffle(password_characters)

    return "".join(password_characters)


def check_strength(password):
    """Return (label, fraction) where fraction is between 0 and 1."""
    has_upper = any(char.isupper() for char in password)
    has_lower = any(char.islower() for char in password)
    has_digit = any(char.isdigit() for char in password)
    has_symbol = any(char in string.punctuation for char in password)

    variety_points = sum([has_upper, has_lower, has_digit, has_symbol])

    length_points = 0
    if len(password) >= 12:
        length_points += 1
    if len(password) >= 16:
        length_points += 1

    score = variety_points + length_points  # maximum is 6

    if score <= 3:
        label = "Weak"
    elif score == 4:
        label = "Medium"
    else:
        label = "Strong"

    return label, score / 6


def add_to_history(history, password):
    """Add a password to the front of the history, keeping only the last 5."""
    history.insert(0, password)
    del history[MAX_HISTORY:]


if __name__ == "__main__":
    # Quick self-test: runs only when this file is run directly
    sets = get_character_sets(True, True, True, True, exclude_ambiguous=True)
    test_password = generate_password(16, sets)
    print("Password:", test_password)
    print("Strength:", check_strength(test_password))

    test_history = []
    for _ in range(7):
        add_to_history(test_history, generate_password(10, sets))
    print("History size:", len(test_history))
    print("History:", test_history)