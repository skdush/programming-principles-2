def square(n):
    for i in range(14, n + 1):
        yield i ** 2
n = int(input())
for i in square(n):
    print(i)