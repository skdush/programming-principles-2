import json

FILE = "sample-data.json"

def iter_attribute_blocks(obj):
    """
    Recursively yield dicts that look like ACI-style attribute blocks:
    {"attributes": {...}} anywhere in the JSON tree.
    """
    if isinstance(obj, dict):
        if "attributes" in obj and isinstance(obj["attributes"], dict):
            yield obj["attributes"]
        for v in obj.values():
            yield from iter_attribute_blocks(v)
    elif isinstance(obj, list):
        for item in obj:
            yield from iter_attribute_blocks(item)

def get_desc(attrs: dict) -> str:
    # some JSON use 'descr', some 'description'
    return attrs.get("descr") or attrs.get("description") or ""

def main():
    with open(FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    rows = []
    for attrs in iter_attribute_blocks(data):
        dn = attrs.get("dn")
        if not dn:
            continue
        desc = get_desc(attrs)
        speed = attrs.get("speed", "")
        mtu = attrs.get("mtu", "")
        rows.append((str(dn), str(desc), str(speed), str(mtu)))

    # Optional: keep only physical interface DNs like in sample (comment out if not needed)
    # rows = [r for r in rows if "/sys/phys-[" in r[0]]

    # Sort by DN (nice, stable output)
    rows.sort(key=lambda x: x[0])

    # Column widths similar to the sample output
    dn_w, desc_w, speed_w, mtu_w = 50, 20, 8, 6

    print("Interface Status")
    print("=" * 80)
    print(f'{"DN":<{dn_w}} {"Description":<{desc_w}} {"Speed":<{speed_w}} {"MTU":<{mtu_w}}')
    print(f'{"-"*dn_w} {"-"*desc_w} {"-"*speed_w} {"-"*mtu_w}')

    for dn, desc, speed, mtu in rows:
        print(f"{dn:<{dn_w}} {desc:<{desc_w}} {speed:<{speed_w}} {mtu:<{mtu_w}}")

if __name__ == "__main__":
    main()
