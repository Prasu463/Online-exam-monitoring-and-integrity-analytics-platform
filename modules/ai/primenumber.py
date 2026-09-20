lower = int(input("enter lower bound:"))
upper = int(input("enter upper bound:"))

print("prime number between", lower, "and", upper, "are:")

for num in range(lower, upper+1):
    if num > 1:
        is_prime = True

        for i in range(2, int(num**0.5)+1):
            if (num % i) == 0:
                is_prime = False
                break

        if is_prime:
            print(num, end=" ")