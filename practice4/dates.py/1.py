from datetime import datetime, timedelta

today = datetime.now()
print((today - timedelta(days=5)).date())
