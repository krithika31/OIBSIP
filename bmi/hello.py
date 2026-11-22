
print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
print("        BMI CALCULATOR")
print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
print("Heyyy! Let's check your BMI. ")
print()

while True:

    try:
        weight = float(input("Enter your weight in kg: "))
        height = float(input("Enter your height in cm: "))

        if weight <= 0 or height <= 0:
            print("Invalid values! Please enter positive weight and height.")

        else:
            height = height / 100

            bmi = weight / (height * height)

            print("\n---------- YOUR RESULT ----------")
            print("Weight:", weight, "kg")
            print("Height:", height * 100, "cm")
            print("Your BMI:", round(bmi, 2))

            if bmi < 18.5:
                print("Category: Underweight")
                print("Your BMI is a little below the healthy range. Focus on nourishing your body.")

            elif bmi < 25:
                print("Category: Normal")
                print("You're in the healthy BMI range! Keep maintaining those healthy habits.")

            elif bmi < 30:
                print("Category: Overweight")
                print("Your BMI is slightly above the healthy range. Small steps towards a healthier you can make a difference.")

            else:
                print("Category: Obese")
                print("Your BMI is above the healthy range. Let's work towards a healthier lifestyle.")

    except ValueError:
        print("Please enter numbers only!")

    print()
    again = input("Do you want to calculate BMI again? (yes/no): ")

    if again.lower() != "yes":
        print("\n*------------------------------------------------*")
        print("Thank you for using BMI Calculator!")
        print("See you next time! Keep prioritizing your health!!")
        print("*------------------------------------------------*")
        break
