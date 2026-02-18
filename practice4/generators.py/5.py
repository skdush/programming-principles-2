def rbackwards(n):
    for i in range(n, 0, -1):
        yield i
n = int(input())
print(list(rbackwards(n)))