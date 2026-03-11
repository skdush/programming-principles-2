from functools import reduce

numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

# ──────────────────────────────────────────
# Пример 1: map — умножить каждый элемент на 2
# ──────────────────────────────────────────
doubled = list(map(lambda x: x * 2, numbers))
print("map (x2):", doubled)
# [2, 4, 6, 8, 10, 12, 14, 16, 18, 20]

# ──────────────────────────────────────────
# Пример 2: map — перевести строки в верхний регистр
# ──────────────────────────────────────────
words = ["hello", "world", "python"]
upper = list(map(str.upper, words))
print("map (upper):", upper)
# ['HELLO', 'WORLD', 'PYTHON']

# ──────────────────────────────────────────
# Пример 3: filter — оставить только чётные числа
# ──────────────────────────────────────────
evens = list(filter(lambda x: x % 2 == 0, numbers))
print("filter (чётные):", evens)
# [2, 4, 6, 8, 10]

# ──────────────────────────────────────────
# Пример 4: filter — оставить только длинные слова
# ──────────────────────────────────────────
words2 = ["cat", "elephant", "dog", "butterfly", "ox"]
long_words = list(filter(lambda w: len(w) > 3, words2))
print("filter (длина > 3):", long_words)
# ['elephant', 'butterfly']

# ──────────────────────────────────────────
# Пример 5: reduce — сумма всех чисел
# ──────────────────────────────────────────
total = reduce(lambda a, b: a + b, numbers)
print("reduce (сумма):", total)
# 55