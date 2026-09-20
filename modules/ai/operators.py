a = 15
b = 4

print(f"Given values: a={a}, b={b}\n" + "-" * 30)

# 1. Addition(+)
sum_result = (a + b)
print(f"Addition(a+b): {sum_result}")

# 2. Subtraction(-)
sub_result = (a - b)
print(f"Subtraction(a-b): {sub_result}")

# 3. Multiplication(*)
mul_result = (a * b)
print(f"Multiplication(a*b): {mul_result}")

# 4. Standard division(/)
div_result = a / b
print(f"Division(a/b): {div_result}")

# 5. Floor Division(//)
floor_div_result = a // b
print(f"Floor division(a//b): {floor_div_result}")

# 6. Modulus(%)
mod_result = a % b
print(f"Modulus/Remainder(a%b): {mod_result}")

# 7. Exponentiation(**)
exp_result = a ** b
print(f"Exponentiation(a**b): {exp_result}")
            # ii) Relational operator
x, y = 10, 20

print(x == y)
print(x != y)
print(x > y)
print(x < y)
print(x >= 10)
print(x <= 15)


# iii) Assignment operator
num = 10

num += 5
print("num += 5:", num)

num -= 3
print("num -= 3:", num)

num *= 2
print("num *= 2:", num)

num /= 1
print("num /= 1:", num)


# iv) Logical operator
a = True
b = False

print(a and b)
print(a or b)
print(not a)


# v) Bitwise
a, b = 6, 3

print(a & b)
print(a | b)
print(a ^ b)
print(~a)
print(a << 1)
print(a >> 1)
# vi) Ternary operator
age = 20
status = "adult" if age >= 18 else "minor"
print(status)


# vii) Membership operator
fruits = ["apple", "banana", "cherry"]

print("banana" in fruits)
print("orange" not in fruits)


# viii) Identity operator
x = [1, 2, 3]
y = [1, 2, 3]
z = x

print(x is z)
print(x is y)
print(x is not y)