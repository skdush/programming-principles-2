import json
import csv
from connect import get_connection

def execute_query(query, params=None, fetch=False):
    conn = get_connection()
    if not conn: return None
    try:
        with conn.cursor() as cur:
            cur.execute(query, params)
            if fetch:
                return cur.fetchall()
            conn.commit()
    except Exception as e:
        print(f"SQL Error: {e}")
        conn.rollback()
    finally:
        conn.close()

def export_to_json(filename="contacts.json"):
    query = """
        SELECT c.name, c.email, c.birthday::TEXT, g.name,
               COALESCE(json_agg(json_build_object('phone', p.phone, 'type', p.type)) FILTER (WHERE p.phone IS NOT NULL), '[]')
        FROM contacts c
        LEFT JOIN groups g ON c.group_id = g.id
        LEFT JOIN phones p ON c.id = p.contact_id
        GROUP BY c.id, g.name
    """
    rows = execute_query(query, fetch=True)
    if not rows: return

    data = [{"name": r[0], "email": r[1], "birthday": r[2], "group": r[3], "phones": r[4]} for r in rows]
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)
    print(f"Exported {len(data)} contacts to {filename}.")

def import_from_json(filename="contacts.json"):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("File not found.")
        return

    conn = get_connection()
    cur = conn.cursor()
    try:
        for contact in data:
            cur.execute("SELECT id FROM contacts WHERE name = %s", (contact['name'],))
            if cur.fetchone():
                action = input(f"Contact '{contact['name']}' exists. Overwrite (o) or Skip (s)? [o/s]: ").lower()
                if action == 's': continue
                cur.execute("DELETE FROM contacts WHERE name = %s", (contact['name'],))

            group_id = None
            if contact.get('group'):
                cur.execute("INSERT INTO groups (name) VALUES (%s) ON CONFLICT (name) DO NOTHING", (contact['group'],))
                cur.execute("SELECT id FROM groups WHERE name = %s", (contact['group'],))
                group_id = cur.fetchone()[0]

            birthday = contact.get('birthday') if contact.get('birthday') else None
            cur.execute(
                "INSERT INTO contacts (name, email, birthday, group_id) VALUES (%s, %s, %s::DATE, %s) RETURNING id",
                (contact['name'], contact.get('email'), birthday, group_id)
            )
            contact_id = cur.fetchone()[0]

            for p in contact.get('phones', []):
                cur.execute("INSERT INTO phones (contact_id, phone, type) VALUES (%s, %s, %s)",
                            (contact_id, p['phone'], p['type']))
        conn.commit()
        print("JSON import complete.")
    except Exception as e:
        conn.rollback()
        print(f"Error: {e}")
    finally:
        conn.close()

def import_csv(filename="contacts.csv"):
    conn = get_connection()
    cur = conn.cursor()
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                group_id = None
                if row.get('group'):
                    cur.execute("INSERT INTO groups (name) VALUES (%s) ON CONFLICT (name) DO NOTHING", (row['group'],))
                    cur.execute("SELECT id FROM groups WHERE name = %s", (row['group'],))
                    group_id = cur.fetchone()[0]

                birthday = row['birthday'] if row.get('birthday') else None
                cur.execute(
                    "INSERT INTO contacts (name, email, birthday, group_id) VALUES (%s, %s, %s::DATE, %s) ON CONFLICT (name) DO NOTHING RETURNING id",
                    (row['name'], row.get('email'), birthday, group_id)
                )
                res = cur.fetchone()
                if res and row.get('phone'):
                    cur.execute("INSERT INTO phones (contact_id, phone, type) VALUES (%s, %s, %s)",
                                (res[0], row['phone'], row.get('type', 'mobile')))
        conn.commit()
        print("CSV import complete.")
    except Exception as e:
        conn.rollback()
        print(f"Error: {e}")
    finally:
        conn.close()


def view_contacts_paginated():
    print("\n--- Sort & Filter Options ---")
    sort_opts = {"1": "name", "2": "birthday", "3": "created_at"}
    sort_choice = input("Sort by (1: Name, 2: Birthday, 3: Date Added) [default 1]: ")
    sort_col = sort_opts.get(sort_choice, "name")

    group_filter = input("Filter by Group name (leave empty for all): ").strip()

    limit = 3
    offset = 0

    while True:
        query = f"""
            SELECT c.name, c.email, c.birthday, g.name
            FROM contacts c
            LEFT JOIN groups g ON c.group_id = g.id
        """
        params = []
        if group_filter:
            query += " WHERE g.name ILIKE %s"
            params.append(group_filter)

        query += f" ORDER BY c.{sort_col} NULLS LAST LIMIT %s OFFSET %s"
        params.extend([limit, offset])

        rows = execute_query(query, tuple(params), fetch=True)

        print(f"\n--- Page {offset//limit + 1} ---")
        if not rows:
            print("No contacts found.")
        else:
            for r in rows:
                print(f"Name: {r[0]} | Email: {r[1]} | B-Day: {r[2]} | Group: {r[3]}")

        cmd = input("\nCommands: [n]ext, [p]rev, [q]uit: ").lower()
        if cmd == 'n' and len(rows) == limit: offset += limit
        elif cmd == 'p': offset = max(0, offset - limit)
        elif cmd == 'q': break

def search_console():
    q = input("Search term (name/email/phone): ")
    rows = execute_query("SELECT * FROM search_contacts(%s)", (q,), fetch=True)
    for r in rows:
        print(f"Match: {r[0]} | {r[1]} | Phone: {r[2]} ({r[3]})")


def add_phone_procedure():
    name = input("Contact name: ")
    phone = input("Phone number: ")
    p_type = input("Type (home/work/mobile): ")
    execute_query("CALL add_phone(%s, %s, %s)", (name, phone, p_type))
    print("Phone added (if contact exists).")

def move_group_procedure():
    name = input("Contact name: ")
    group = input("New group name: ")
    execute_query("CALL move_to_group(%s, %s)", (name, group))
    print("Group updated.")


def main():
    while True:
        print("\n=== PhoneBook Extended ===")
        print("1. View Contacts (Sort/Filter/Pagination)")
        print("2. Search Contacts")
        print("3. Add Phone to Contact (Procedure)")
        print("4. Move to Group (Procedure)")
        print("5. Export JSON")
        print("6. Import JSON")
        print("7. Import CSV")
        print("0. Exit")

        c = input("Choose: ")
        if c == '1': view_contacts_paginated()
        elif c == '2': search_console()
        elif c == '3': add_phone_procedure()
        elif c == '4': move_group_procedure()
        elif c == '5': export_to_json()
        elif c == '6': import_from_json()
        elif c == '7': import_csv()
        elif c == '0': break

if __name__ == '__main__':
    main()
