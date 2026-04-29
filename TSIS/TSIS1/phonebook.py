import csv
import json
import os
from connect import get_connection

PAGE  = 5
DIR   = os.path.dirname(os.path.abspath(__file__))


def _sql(name):
    with open(os.path.join(DIR, name), encoding="utf-8") as f:
        return f.read()


def init_db():
    conn = get_connection()
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute(_sql("schema.sql"))
    cur.execute(_sql("procedures.sql"))
    cur.close()
    conn.close()


def _run(sql, params=()):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)


def _fetch(sql, params=()):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            return cur.fetchall()


def _paginate(rows, headers):
    if not rows:
        print("  No results.")
        return
    w = 15
    print("\n" + "  ".join(str(h).ljust(w) for h in headers))
    print("-" * (w * len(headers) + 2 * (len(headers) - 1)))
    total = (len(rows) + PAGE - 1) // PAGE
    page  = 0
    while True:
        for r in rows[page * PAGE : page * PAGE + PAGE]:
            print("  ".join(str(v or "").ljust(w) for v in r))
        print(f"\n  Page {page+1}/{total}  [{len(rows)} total]")
        if total <= 1:
            break
        cmd = input("  n=next  p=prev  q=quit > ").strip().lower()
        if cmd == "n" and page < total - 1:
            page += 1
        elif cmd == "p" and page > 0:
            page -= 1
        elif cmd == "q":
            break


def insert_from_csv():
    path = os.path.join(DIR, "contacts.csv")
    with get_connection() as conn:
        with conn.cursor() as cur:
            n = 0
            for row in csv.DictReader(open(path, encoding="utf-8")):
                cur.execute("""
                    INSERT INTO phonebook (username, first_name, last_name, phone, email, birthday)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (username) DO NOTHING
                """, (row.get("username"), row.get("first_name"), row.get("last_name"),
                      row.get("phone"), row.get("email") or None, row.get("birthday") or None))
                n += 1
    print(f"  CSV imported: {n} rows.")


def add_contact():
    username = input("  Username: ").strip()
    fname    = input("  First name: ").strip()
    lname    = input("  Last name: ").strip()
    phone    = input("  Phone: ").strip()
    email    = input("  Email (optional): ").strip() or None
    bday     = input("  Birthday YYYY-MM-DD (optional): ").strip() or None
    _run("""INSERT INTO phonebook (username, first_name, last_name, phone, email, birthday)
            VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT (username) DO NOTHING""",
         (username, fname, lname, phone, email, bday))
    print("  Contact added.")


def update_contact():
    username = input("  Username: ").strip()
    fields   = {"1": "first_name", "2": "last_name", "3": "phone", "4": "email", "5": "birthday"}
    print("  1-first_name  2-last_name  3-phone  4-email  5-birthday")
    col = fields.get(input("  Choice: ").strip())
    if not col:
        print("  Invalid."); return
    val = input(f"  New {col}: ").strip() or None
    _run(f"UPDATE phonebook SET {col}=%s WHERE username=%s", (val, username))
    print("  Updated.")


def delete_contact():
    print("  1-by username  2-by phone")
    c = input("  Choice: ").strip()
    if c == "1":
        _run("CALL delete_contact(p_username => %s)", (input("  Username: ").strip(),))
    elif c == "2":
        _run("CALL delete_contact(p_phone => %s)", (input("  Phone: ").strip(),))
    print("  Deleted.")


def add_phone():
    user  = input("  Username: ").strip()
    phone = input("  Phone number: ").strip()
    ptype = input("  Type (home/work/mobile): ").strip()
    _run("CALL add_phone(%s, %s, %s)", (user, phone, ptype))
    print("  Phone added.")


def move_to_group():
    user  = input("  Username: ").strip()
    print("  Groups: Family, Work, Friend, Other")
    group = input("  Group: ").strip()
    _run("CALL move_to_group(%s, %s)", (user, group))
    print("  Moved.")


def search_contacts():
    SORT = {"1": "pb.first_name", "2": "pb.birthday", "3": "pb.id"}
    BASE = """SELECT pb.id, pb.username, pb.first_name, pb.last_name,
                     pb.phone, pb.email, pb.birthday::TEXT, g.name
              FROM phonebook pb LEFT JOIN groups g ON g.id = pb.group_id"""

    print("  Filter: 1-name  2-phone prefix  3-group  4-email  5-all")
    flt  = input("  Choice: ").strip()
    print("  Sort:   1-name  2-birthday  3-date added")
    srt  = SORT.get(input("  Sort: ").strip(), "pb.first_name")

    if flt == "1":
        name = input("  Name: ").strip()
        rows = _fetch(BASE + f" WHERE pb.first_name ILIKE %s OR pb.last_name ILIKE %s ORDER BY {srt}",
                      (f"%{name}%", f"%{name}%"))
    elif flt == "2":
        pfx  = input("  Phone prefix: ").strip()
        rows = _fetch(BASE + f""" WHERE pb.phone LIKE %s
                                     OR EXISTS (SELECT 1 FROM phones ph
                                                WHERE ph.contact_id=pb.id AND ph.phone LIKE %s)
                                  ORDER BY {srt}""", (f"{pfx}%", f"{pfx}%"))
    elif flt == "3":
        grp  = input("  Group: ").strip()
        rows = _fetch(BASE + f" WHERE g.name ILIKE %s ORDER BY {srt}", (f"%{grp}%",))
    elif flt == "4":
        em   = input("  Email (partial): ").strip()
        rows = _fetch(BASE + f" WHERE pb.email ILIKE %s ORDER BY {srt}", (f"%{em}%",))
    else:
        rows = _fetch(BASE + f" ORDER BY {srt}")

    _paginate(rows, ["ID", "Username", "First", "Last", "Phone", "Email", "Birthday", "Group"])


def search_pattern():
    pattern = input("  Pattern: ").strip()
    rows    = _fetch("SELECT * FROM search_contacts(%s)", (pattern,))
    seen, uniq = set(), []
    for r in rows:
        if r[0] not in seen:
            seen.add(r[0]); uniq.append(r)
    _paginate(uniq, ["ID", "Username", "First", "Last", "Email", "Birthday", "Group", "Phone", "Type"])


def export_json():
    rows = _fetch("""
        SELECT pb.id, pb.username, pb.first_name, pb.last_name, pb.phone,
               pb.email, pb.birthday::TEXT, g.name,
               COALESCE(json_agg(json_build_object('phone', ph.phone, 'type', ph.type))
                        FILTER (WHERE ph.id IS NOT NULL), '[]')
        FROM phonebook pb
        LEFT JOIN groups g  ON g.id = pb.group_id
        LEFT JOIN phones ph ON ph.contact_id = pb.id
        GROUP BY pb.id, pb.username, pb.first_name, pb.last_name, pb.phone,
                 pb.email, pb.birthday, g.name
        ORDER BY pb.username
    """)
    data = [{"id": r[0], "username": r[1], "first_name": r[2], "last_name": r[3],
             "phone": r[4], "email": r[5], "birthday": r[6], "group": r[7], "phones": r[8]}
            for r in rows]
    fname = input("  Filename [contacts_export.json]: ").strip() or "contacts_export.json"
    with open(fname, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"  Exported {len(data)} contacts → {fname}")


def import_json():
    fname = input("  Filename [contacts_export.json]: ").strip() or "contacts_export.json"
    try:
        with open(fname, encoding="utf-8") as f:
            contacts = json.load(f)
    except FileNotFoundError:
        print("  File not found."); return
    print("  On duplicate: 1-skip  2-overwrite")
    dup   = input("  Choice: ").strip()
    added = skipped = 0
    with get_connection() as conn:
        with conn.cursor() as cur:
            for c in contacts:
                cur.execute("SELECT id FROM phonebook WHERE username=%s", (c["username"],))
                if cur.fetchone():
                    if dup == "2":
                        cur.execute("""UPDATE phonebook SET first_name=%s, last_name=%s,
                                        phone=%s, email=%s, birthday=%s WHERE username=%s""",
                                    (c.get("first_name"), c.get("last_name"), c.get("phone"),
                                     c.get("email"), c.get("birthday"), c["username"]))
                        added += 1
                    else:
                        skipped += 1
                else:
                    cur.execute("""INSERT INTO phonebook (username, first_name, last_name,
                                   phone, email, birthday) VALUES (%s,%s,%s,%s,%s,%s)""",
                                (c["username"], c.get("first_name"), c.get("last_name"),
                                 c.get("phone"), c.get("email"), c.get("birthday")))
                    added += 1
    print(f"  Imported: {added}, Skipped: {skipped}.")


MENU = {
    "1":  ("Import from CSV",             insert_from_csv),
    "2":  ("Add contact",                 add_contact),
    "3":  ("Update contact",              update_contact),
    "4":  ("Delete contact",              delete_contact),
    "5":  ("Search / filter + sort",      search_contacts),
    "6":  ("Search by pattern (all fields + phones)", search_pattern),
    "7":  ("Add extra phone number",      add_phone),
    "8":  ("Move contact to group",       move_to_group),
    "9":  ("Export to JSON",              export_json),
    "10": ("Import from JSON",            import_json),
}


def menu():
    init_db()
    while True:
        print("\n=== PhoneBook TSIS1 ===")
        for k, (label, _) in MENU.items():
            print(f"  {k:>2}. {label}")
        print("   0. Exit")
        choice = input("Choice: ").strip()
        if choice == "0":
            break
        if choice in MENU:
            try:
                MENU[choice][1]()
            except Exception as e:
                print(f"  Error: {e}")


if __name__ == "__main__":
    menu()
