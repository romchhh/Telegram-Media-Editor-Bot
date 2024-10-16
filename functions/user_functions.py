import random


def generate_math_question():
    num1 = random.randint(2, 20)
    num2 = random.randint(1, 20)
    correct_answer = num1 + num2
    return num1, num2, correct_answer