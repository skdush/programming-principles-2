from datetime import datetime, timedelta
time_now = datetime.now()

time_future = time_now + timedelta(minutes=100000)

print(time_future)