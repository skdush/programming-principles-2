from datetime import datetime

d1 = datetime(2025, 1, 1, 12, 0, 0)
d2 = datetime(2025, 1, 2, 12, 0, 0)

diff = (d2 - d1).total_seconds()

print(diff)
