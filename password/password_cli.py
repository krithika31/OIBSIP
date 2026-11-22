import random
import string

MIN_LENGTH = 8


def ask_for_length():
    """Keep asking until the user types a valid password length."""
    while True:
        user_input = input("Enter password length (minimum 8): ")

        try:
            length = int(user_input)
        except ValueError:
            print("Please enter a whole number, like 12.")
            continue

        if length < MIN_LENGTH:
            print(f"Password must be at least {MIN_LENGTH} characters long.")
            continue

        return length


def ask_yes_no(question):
    """Ask a yes/no question and return True for yes, False for no."""
    while True:
        answer = input(question + " (y/n): ").strip().lower()
        if answer == "y":
            return True
        if answer == "n":
            return False
        print("Please type y or n.")


def ask_for_character_types():
    """Ask which character types to include. At least 2 are required."""
    while True:
        chosen = {
            "uppercase": ask_yes_no("Include uppercase letters?"),
            "lowercase": ask_yes_no("Include lowercase letters?"),
            "numbers": ask_yes_no("Include numbers?"),
            "symbols": ask_yes_no("Include symbols?"),
        }

        if sum(chosen.values()) >= 2:
            return chosen

        print("Please choose at least 2 character types. Let's try again.\n")


def build_character_sets(chosen_types):
    """Return a list of the character sets the user selected."""
    selected_sets = []

    if chosen_types["uppercase"]:
        selected_sets.append(string.ascii_uppercase)
    if chosen_types["lowercase"]:
        selected_sets.append(string.ascii_lowercase)
    if chosen_types["numbers"]:
        selected_sets.append(string.digits)
    if chosen_types["symbols"]:
        selected_sets.append(string.punctuation)

    return selected_sets


def generate_password(length, selected_sets):
    """Create a password that contains every selected character type."""
    password_characters = []

    # Step 1: take one random character from each selected set
    for character_set in selected_sets:
        password_characters.append(random.choice(character_set))

    # Step 2: fill the remaining spaces from all selected characters
    all_characters = "".join(selected_sets)
    while len(password_characters) < length:
        password_characters.append(random.choice(all_characters))

    # Step 3: shuffle so the guaranteed characters aren't always at the start
    random.shuffle(password_characters)

    return "".join(password_characters)


def main():
    print("=" * 40)
    print("      RANDOM PASSWORD GENERATOR")
    print("=" * 40)

    while True:
        length = ask_for_length()
        chosen_types = ask_for_character_types()
        selected_sets = build_character_sets(chosen_types)

        password = generate_password(length, selected_sets)
        print("\nYour password is:", password, "\n")

        if not ask_yes_no("Generate another password?"):
            print("Goodbye! Stay safe online.")
            break


if __name__ == "__main__":
    main()