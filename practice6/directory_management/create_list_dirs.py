import os

# ──────────────────────────────────────────
# Пример 1: Создать одну папку
# ──────────────────────────────────────────
os.mkdir("photos")
print("✔ Создана папка: photos")

# ──────────────────────────────────────────
# Пример 2: Создать вложенные папки
# ──────────────────────────────────────────
os.makedirs("projects/python/homework", exist_ok=True)
print("✔ Создана структура: projects/python/homework")

# ──────────────────────────────────────────
# Пример 3: Список файлов и папок
# ──────────────────────────────────────────
print("\nСодержимое текущей папки:")
for item in os.listdir("."):
    print(" -", item)

# ──────────────────────────────────────────
# Пример 4: Список с пометкой FILE / DIR
# ──────────────────────────────────────────
print("\nС типами:")
for item in os.listdir("."):
    kind = "DIR " if os.path.isdir(item) else "FILE"
    print(f"  [{kind}]  {item}")

# ──────────────────────────────────────────
# Пример 5: Список всех файлов рекурсивно
# ──────────────────────────────────────────
print("\nВсе файлы внутри 'projects':")
for root, dirs, files in os.walk("projects"):
    for file in files:
        print(" ", os.path.join(root, file))
    for d in dirs:
        print("  📁", os.path.join(root, d))

# Очистка
import shutil
shutil.rmtree("photos")
shutil.rmtree("projects")