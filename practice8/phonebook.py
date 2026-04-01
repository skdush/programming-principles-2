from connect import get_connection

def create_table():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS phonebook (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    first_name VARCHAR(50),
                    last_name VARCHAR(50),
                    phone VARCHAR(20) NOT NULL
                )
            """)

def insert_from_csv(filename):
    import csv
    with get_connection() as conn:
        with conn.cursor() as cur:
            with open(filename, encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    cur.execute("""
                        INSERT INTO phonebook (username, first_name, last_name, phone)
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT (username) DO NOTHING
                    """, (row['username'], row['first_name'], row['last_name'], row['phone']))

def insert_from_console():
    username = input("Username: ")
    first_name = input("First name: ")
    last_name = input("Last name: ")
    phone = input("Phone: ")
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO phonebook (username, first_name, last_name, phone)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (username) DO NOTHING
            """, (username, first_name, last_name, phone))


def update_contact():
    username = input("Введи username контакта: ")
    print("Что обновить? 1 - имя, 2 - телефон")
    choice = input("Выбор: ")
    with get_connection() as conn:
        with conn.cursor() as cur:
            if choice == "1":
                new_name = input("Новое имя: ")
                cur.execute("UPDATE phonebook SET first_name=%s WHERE username=%s", (new_name, username))
            elif choice == "2":
                new_phone = input("Новый телефон: ")
                cur.execute("UPDATE phonebook SET phone=%s WHERE username=%s", (new_phone, username))

def query_contacts():
    print("Фильтр: 1 - по имени, 2 - по префиксу телефона, 3 - все")
    choice = input("Выбор: ")
    with get_connection() as conn:
        with conn.cursor() as cur:
            if choice == "1":
                name = input("Имя: ")
                cur.execute("SELECT * FROM phonebook WHERE first_name ILIKE %s", (f"%{name}%",))
            elif choice == "2":
                prefix = input("Префикс телефона: ")
                cur.execute("SELECT * FROM phonebook WHERE phone LIKE %s", (f"{prefix}%",))
            else:
                cur.execute("SELECT * FROM phonebook ORDER BY username")
            rows = cur.fetchall()
            for row in rows:
                print(row)
def delete_contact():
    print("Удалить по: 1 - username, 2 - телефону")
    choice = input("Выбор: ")
    with get_connection() as conn:
        with conn.cursor() as cur:
            if choice == "1":
                username = input("Username: ")
                cur.execute("CALL delete_contact(p_username => %s)", (username,))
            elif choice == "2":
                phone = input("Телефон: ")
                cur.execute("CALL delete_contact(p_phone => %s)", (phone,))

def search_by_pattern():
    pattern = input("Введи паттерн для поиска: ")
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM search_phonebook(%s)", (pattern,))
            rows = cur.fetchall()
            if rows:
                for row in rows:
                    print(row)
            else:
                print("Ничего не найдено.")

def upsert_contact():
    username = input("Username: ")
    first_name = input("First name: ")
    last_name = input("Last name: ")
    phone = input("Phone: ")
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "CALL upsert_contact(%s, %s, %s, %s)",
                (username, first_name, last_name, phone)
            )
    print("Контакт добавлен/обновлён.")

def bulk_insert():
    print("Введи данные (username:phone), по одному на строку. Пустая строка — конец.")
    usernames = []
    phones = []
    while True:
        line = input("username:phone > ").strip()
        if not line:
            break
        parts = line.split(":")
        if len(parts) == 2:
            usernames.append(parts[0].strip())
            phones.append(parts[1].strip())
        else:
            print("Неверный формат, пропускаю.")

    if not usernames:
        print("Нет данных для вставки.")
        return

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "CALL bulk_insert(%s::VARCHAR[], %s::VARCHAR[], NULL)",
                (usernames, phones)
            )
    print("Готово.")

def paginated_query():
    try:
        limit = int(input("Сколько записей на странице? "))
        page = int(input("Номер страницы (с 1): "))
    except ValueError:
        print("Введи числа.")
        return
    offset = (page - 1) * limit
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM get_phonebook_page(%s, %s)", (limit, offset))
            rows = cur.fetchall()
            if rows:
                for row in rows:
                    print(row)
            else:
                print("Записей нет.")


def menu():
    create_table()
    while True:
        print("\n=== PhoneBook ===")
        print("1. Загрузить из CSV")
        print("2. Добавить вручную")
        print("3. Обновить контакт")
        print("4. Найти контакты")
        print("5. Удалить контакт")
        print("6. Поиск по паттерну")
        print("7. Upsert контакт")
        print("8. Bulk insert")
        print("9. Просмотр с пагинацией")
        print("0. Выход")
        choice = input("Выбор: ")
        if choice == "1":
            insert_from_csv("contacts.csv")
        elif choice == "2":
            insert_from_console()
        elif choice == "3":
            update_contact()
        elif choice == "4":
            query_contacts()
        elif choice == "5":
            delete_contact()
        elif choice == "6":
            search_by_pattern()
        elif choice == "7":
            upsert_contact()
        elif choice == "8":
            bulk_insert()
        elif choice == "9":
            paginated_query()
        elif choice == "0":
            break

if __name__ == "__main__":
    menu()