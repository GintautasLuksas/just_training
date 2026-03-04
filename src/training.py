import random
food = []


for _ in range(5):
    user_choice = str(input(f'Please write your favourite food nr{_+1}: '))
    food.append(user_choice)

print(food)


numbers = []

for i in range(10):
    generated = random.randint(1,10)
    numbers.append(generated)

print(numbers)