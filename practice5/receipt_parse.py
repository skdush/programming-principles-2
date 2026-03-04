import re
import json

with open("raw.txt", "r", encoding="utf-8") as f:
    text = f.read()

# 1. Extract prices (берём только строки "Стоимость")
prices = re.findall(r"Стоимость\s*\n([\d\s]+,\d{2})", text)
price_numbers = [float(p.replace(" ", "").replace(",", ".")) for p in prices]

# 2. Extract product names
products = re.findall(r"\d+\.\s*\n(.+)", text)

# 3. Extract total amount
total_match = re.search(r"ИТОГО:\s*\n?([\d\s]+,\d{2})", text)
total = total_match.group(1) if total_match else None

# 4. Extract date and time
datetime_match = re.search(r"Время:\s*([\d\.]+\s[\d:]+)", text)
datetime = datetime_match.group(1) if datetime_match else None

# 5. Extract payment method
payment_match = re.search(r"Банковская карта", text)
payment_method = payment_match.group(0) if payment_match else None

# Structured output
result = {
    "products": products,
    "prices": price_numbers,
    "total": total,
    "date_time": datetime,
    "payment_method": payment_method
}

print(json.dumps(result, indent=4, ensure_ascii=False))