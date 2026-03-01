age = int(input('Please enter your age: '))

if age <= 13:
    print('Child')
elif age >= 13 or age > 18:
    print('You are teen')
else:
    print('You are adult')