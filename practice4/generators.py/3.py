def divisin(n):
    for i in range(0, n + 1):
        if i % 3 == 0 and i % 4 == 0:
            yield i
n = int(input())
print(",".join(str(x) for x in divisin(n)))