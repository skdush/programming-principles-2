import os
import shutil

# Подготовка: создаём тестовые файлы и папки
os.makedirs("source", exist_ok=True)
os.makedirs("destination", exist_ok=True)
os.makedirs("archive", exist_ok=True)
for name in ["report.txt", "photo.jpg", "notes.txt", "data.csv"]:
    open(f"source/{name}", "w").close()

# ──────────────────────────────────────────
# Пример 1: Переместить один файл
# ──────────────────────────────────────────
shutil.move("source/report.txt", "destination/report.txt")
print("✔ Перемещён: source/report.txt → destination/")

# ──────────────────────────────────────────
# Пример 2: Переместить файл в другую папку (только папка)
# ──────────────────────────────────────────
shutil.move("source/photo.jpg", "archive")
print("✔ Перемещён: source/photo.jpg → archive/")

# ──────────────────────────────────────────
# Пример 3: Переместить и переименовать одновременно
# ──────────────────────────────────────────
shutil.move("source/notes.txt", "destination/my_notes.txt")
print("✔ Перемещён и переименован: notes.txt → destination/my_notes.txt")

# ──────────────────────────────────────────
# Пример 4: Переместить все .txt файлы из папки
# ──────────────────────────────────────────
os.makedirs("txt_files", exist_ok=True)
for filename in os.listdir("source"):
    if filename.endswith(".txt"):
        shutil.move(f"source/{filename}", f"txt_files/{filename}")
        print(f"✔ Перемещён: {filename} → txt_files/")

# ──────────────────────────────────────────
# Пример 5: Переместить всю папку целиком
# ──────────────────────────────────────────
shutil.move("source", "archive/old_source")
print("✔ Папка перемещена: source → archive/old_source/")

# Очистка
shutil.rmtree("destination")
shutil.rmtree("archive")
shutil.rmtree("txt_files")