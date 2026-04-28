import csv
import json
import os
from connect import get_connection

PAGE_SIZE = 5
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def _read_file(name):
    with open(os.path.join(BASE_DIR, name), encoding="utf-8") as f:
        return f.read()


def init_db():
    conn = get_connection()
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute(_read_file("schema.sql"))
    cur.execute(_read_file("procedures.sql"))
    cur.close()
    conn.close()


def insert_from_csv(filename=None):
    path = filename or os.path.join(BASE_DIR, "contacts.csv")
    with get_connection() as conn:
        with conn.cursor() as cur:
            with open(path, encoding="utf-8") as f:
                reader = csv.DictReader(f)
                count = 0
                for row in reader:
                    cur.execute("""
                        INSERT INTO phonebook (username, first_name, last_name, phone, email, birthday)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        ON CONFLICT (username) DO NOTHING
                    """, (
                        row.get("username"), row.get("first_name"),
                        row.get("last_name"), row.get("phone"),
                        row.get("email") or None,
                        row.get("birthday") or None,
                    ))
                    count += 1
    print(f"CSV imported: {count} rows processed.")


def insert_from_console():
    username   = input("Username: ").strip()
    first_name = input("First name: ").strip()
    last_name  = input("Last name: ").strip()
    phone      = input("Phone: ").strip()
    email      = input("Email (optional): ").strip() or None
    birthday   = input("Birthday YYYY-MM-DD (optional): ").strip() or None
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO phonebook (username, first_name, last_name, phone, email, birthday)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (username) DO NOTHING
            """, (username, first_name, last_name, phone, email, birthday))
    print("Contact added.")


def upsert_contact():
    username   = input("Username: ").strip()
    first_name = input("First name: ").strip()
    last_name  = input("Last name: ").strip()
    phone      = input("Phone: ").strip()
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("CALL upsert_contact(%s, %s, %s, %s)",
                        (username, first_name, last_name, phone))
    print("Done.")


def bulk_insert():
    print("Enter username:phone pairs (empty line to finish):")
    usernames, phones = [], []
    while True:
        line = input("> ").strip()
        if not line:
            break
        parts = line.split(":")
        if len(parts) == 2:
            usernames.append(parts[0].strip())
            phones.append(parts[1].strip())
        else:
            print("Invalid format, skipping.")
    if not usernames:
        print("Nothing to insert.")
        return
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("CALL bulk_insert(%s::VARCHAR[], %s::VARCHAR[], NULL)",
                        (usernames, phones))
    print("Done.")


def update_contact():
    username = input("Username: ").strip()
    print("Update: 1-first_name  2-last_name  3-phone  4-email  5-birthday")
    choice = input("Choice: ").strip()
    field_map = {
        "1": ("first_name", "First name"),
        "2": ("last_name",  "Last name"),
        "3": ("phone",      "Phone"),
        "4": ("email",      "Email"),
        "5": ("birthday",   "Birthday (YYYY-MM-DD)"),
    }
    if choice not in field_map:
        print("Invalid choice.")
        return
    col, label = field_map[choice]
    value = input(f"{label}: ").strip() or None
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(f"UPDATE phonebook SET {col}=%s WHERE username=%s",
                        (value, username))
    print("Updated.")


def delete_contact():
    print("Delete by: 1-username  2-phone")
    choice = input("Choice: ").strip()
    with get_connection() as conn:
        with conn.cursor() as cur:
            if choice == "1":
                username = input("Username: ").strip()
                cur.execute("CALL delete_contact(p_username => %s)", (username,))
            elif choice == "2":
                phone = input("Phone: ").strip()
                cur.execute("CALL delete_contact(p_phone => %s)", (phone,))
    print("Deleted.")


def add_phone():
    username = input("Username: ").strip()
    phone    = input("Phone number: ").strip()
    print("Type: home / work / mobile")
    ptype = input("Type: ").strip()
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("CALL add_phone(%s, %s, %s)", (username, phone, ptype))
    print("Phone added.")


def move_to_group():
    username = input("Username: ").strip()
    print("Available groups: Family, Work, Friend, Other (or enter a new group name)")
    group = input("Group: ").strip()
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("CALL move_to_group(%s, %s)", (username, group))
    print("Contact moved to group.")


def _paginate(rows, headers):
    if not rows:
        print("No results.")
        return
    col_w = 14
    header_line = "  ".join(str(h).ljust(col_w) for h in headers)
    print(f"\n{header_line}")
    print("-" * len(header_line))
    page = 0
    total_pages = (len(rows) + PAGE_SIZE - 1) // PAGE_SIZE
    while True:
        start = page * PAGE_SIZE
        chunk = rows[start: start + PAGE_SIZE]
        for r in chunk:
            print("  ".join(str(v or "").ljust(col_w) for v in r))
        print(f"\n  Page {page+1}/{total_pages}  |  Total: {len(rows)}")
        if total_pages <= 1:
            break
        print("  n=next  p=prev  q=quit")
        cmd = input("  > ").strip().lower()
        if cmd == "n" and start + PAGE_SIZE < len(rows):
            page += 1
        elif cmd == "p" and page > 0:
            page -= 1
        elif cmd == "q":
            break


def query_contacts():
    print("Filter: 1-by name  2-by phone prefix  3-by group  4-by email  5-all")
    choice = input("Choice: ").strip()
    print("Sort: 1-name  2-birthday  3-date added  (default: name)")
    sort = input("Sort: ").strip()
    sort_col = {"1": "pb.first_name", "2": "pb.birthday", "3": "pb.id"}.get(sort, "pb.first_name")

    base_select = f"""
        SELECT pb.id, pb.username, pb.first_name, pb.last_name,
               pb.phone, pb.email, pb.birthday::TEXT, g.name
        FROM phonebook pb
        LEFT JOIN groups g ON g.id = pb.group_id
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            if choice == "1":
                name = input("Name: ").strip()
                cur.execute(
                    base_select + f"WHERE pb.first_name ILIKE %s OR pb.last_name ILIKE %s ORDER BY {sort_col}",
                    (f"%{name}%", f"%{name}%"),
                )
            elif choice == "2":
                prefix = input("Phone prefix: ").strip()
                cur.execute(
                    base_select + f"""
                        WHERE pb.phone LIKE %s
                           OR EXISTS (SELECT 1 FROM phones ph WHERE ph.contact_id=pb.id AND ph.phone LIKE %s)
                        ORDER BY {sort_col}
                    """,
                    (f"{prefix}%", f"{prefix}%"),
                )
            elif choice == "3":
                group = input("Group name: ").strip()
                cur.execute(
                    base_select + f"WHERE g.name ILIKE %s ORDER BY {sort_col}",
                    (f"%{group}%",),
                )
            elif choice == "4":
                email = input("Email (partial): ").strip()
                cur.execute(
                    base_select + f"WHERE pb.email ILIKE %s ORDER BY {sort_col}",
                    (f"%{email}%",),
                )
            else:
                cur.execute(base_select + f"ORDER BY {sort_col}")
            rows = cur.fetchall()
    _paginate(rows, ["ID", "Username", "First", "Last", "Phone", "Email", "Birthday", "Group"])


def search_pattern():
    pattern = input("Search pattern: ").strip()
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM search_contacts(%s)", (pattern,))
            rows = cur.fetchall()
    seen, unique = set(), []
    for r in rows:
        if r[0] not in seen:
            seen.add(r[0])
            unique.append(r)
    _paginate(unique, ["ID", "Username", "First", "Last", "Email", "Birthday", "Group", "Phone", "Type"])


def paginated_query():
    try:
        limit  = int(input("Records per page: "))
        page   = int(input("Page number (from 1): "))
    except ValueError:
        print("Invalid input.")
        return
    offset = (page - 1) * limit
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM get_phonebook_page(%s, %s)", (limit, offset))
            rows = cur.fetchall()
    _paginate(rows, ["ID", "Username", "First", "Last", "Phone"])


def export_to_json():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT pb.id, pb.username, pb.first_name, pb.last_name, pb.phone,
                       pb.email, pb.birthday::TEXT, g.name AS group_name,
                       COALESCE(
                           json_agg(json_build_object('phone', ph.phone, 'type', ph.type))
                           FILTER (WHERE ph.id IS NOT NULL), '[]'
                       ) AS phones
                FROM phonebook pb
                LEFT JOIN groups g  ON g.id = pb.group_id
                LEFT JOIN phones ph ON ph.contact_id = pb.id
                GROUP BY pb.id, pb.username, pb.first_name, pb.last_name, pb.phone,
                         pb.email, pb.birthday, g.name
                ORDER BY pb.username
            """)
            rows = cur.fetchall()
    contacts = [
        {
            "id": r[0], "username": r[1], "first_name": r[2], "last_name": r[3],
            "phone": r[4], "email": r[5], "birthday": r[6], "group": r[7],
            "extra_phones": r[8],
        }
        for r in rows
    ]
    filename = input("Filename (default: contacts_export.json): ").strip() or "contacts_export.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(contacts, f, indent=2, ensure_ascii=False)
    print(f"Exported {len(contacts)} contacts to {filename}.")


def import_from_json():
    filename = input("Filename (default: contacts_export.json): ").strip() or "contacts_export.json"
    try:
        with open(filename, encoding="utf-8") as f:
            contacts = json.load(f)
    except FileNotFoundError:
        print("File not found.")
        return
    print("On duplicate: 1-skip  2-overwrite")
    dup = input("Choice: ").strip()
    imported = skipped = 0
    with get_connection() as conn:
        with conn.cursor() as cur:
            for c in contacts:
                cur.execute("SELECT id FROM phonebook WHERE username=%s", (c["username"],))
                exists = cur.fetchone()
                if exists:
                    if dup == "2":
                        cur.execute("""
                            UPDATE phonebook
                               SET first_name=%s, last_name=%s, phone=%s, email=%s, birthday=%s
                             WHERE username=%s
                        """, (c.get("first_name"), c.get("last_name"), c.get("phone"),
                              c.get("email"), c.get("birthday"), c["username"]))
                        imported += 1
                    else:
                        skipped += 1
                else:
                    cur.execute("""
                        INSERT INTO phonebook (username, first_name, last_name, phone, email, birthday)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (c["username"], c.get("first_name"), c.get("last_name"),
                          c.get("phone"), c.get("email"), c.get("birthday")))
                    imported += 1
    print(f"Imported: {imported}, Skipped: {skipped}.")


def menu():
    init_db()
    while True:
        print("\n=== PhoneBook TSIS1 ===")
        print(" 1. Import from CSV")
        print(" 2. Add contact (console)")
        print(" 3. Upsert contact")
        print(" 4. Bulk insert")
        print(" 5. Update contact")
        print(" 6. Delete contact")
        print(" 7. Search / filter contacts")
        print(" 8. Search by pattern (all fields + phones)")
        print(" 9. Paginated view")
        print("10. Add phone number")
        print("11. Move to group")
        print("12. Export to JSON")
        print("13. Import from JSON")
        print(" 0. Exit")
        choice = input("Choice: ").strip()
        actions = {
            "1":  insert_from_csv,
            "2":  insert_from_console,
            "3":  upsert_contact,
            "4":  bulk_insert,
            "5":  update_contact,
            "6":  delete_contact,
            "7":  query_contacts,
            "8":  search_pattern,
            "9":  paginated_query,
            "10": add_phone,
            "11": move_to_group,
            "12": export_to_json,
            "13": import_from_json,
        }
        if choice == "0":
            break
        action = actions.get(choice)
        if action:
            try:
                action()
            except Exception as e:
                print(f"Error: {e}")


if __name__ == "__main__":
    menu()
