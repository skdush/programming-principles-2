fruits = ["apple", "banana", "cherry", "mango"]
prices = [1.2, 0.5, 2.0, 1.8]
colors = ["red", "yellow", "red", "orange"]

# ──────────────────────────────────────────
# Пример 1: enumerate — вывести список с номерами
# ──────────────────────────────────────────
print("Список фруктов:")
for i, fruit in enumerate(fruits, start=1):
    print(f"  {i}. {fruit}")
# 1. apple
# 2. banana ...

# ──────────────────────────────────────────
# Пример 2: enumerate — найти индекс нужного элемента
# ──────────────────────────────────────────
for i, fruit in enumerate(fruits):
    if fruit == "cherry":
        print(f"\nenumerate — cherry находится на индексе: {i}")
# cherry находится на индексе: 2

# ──────────────────────────────────────────
# Пример 3: zip — объединить два списка в пары
# ──────────────────────────────────────────
print("\nФрукты и цены:")
for fruit, price in zip(fruits, prices):
    print(f"  {fruit}: ${price}")
# apple: $1.2
# banana: $0.5 ...

# ──────────────────────────────────────────
# Пример 4: zip — объединить три списка сразу
# ──────────────────────────────────────────
print("\nФрукт | Цена | Цвет:")
for fruit, price, color in zip(fruits, prices, colors):
    print(f"  {fruit:<10} ${price:<6} {color}")

# ──────────────────────────────────────────
# Пример 5: zip + enumerate вместе
# ──────────────────────────────────────────
print("\nПронумерованные пары:")
for i, (fruit, price) in enumerate(zip(fruits, prices), start=1):
    print(f"  {i}. {fruit} — ${price}")
