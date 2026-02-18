from datetime import datetime

now = datetime.now()
print(now.replace(microsecond=0))
