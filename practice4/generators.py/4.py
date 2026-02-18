def squares(a, b):
    for i in range(a, b + 1):
        yield i ** 2
n, m = map(int, input().split())
print(list(squares(n, m)))