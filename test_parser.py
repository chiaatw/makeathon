import asyncio
from req_gatherer import producer_app
producer_app.set_up()
events = []
for chunk in producer_app.app.stream_query('produce a short list of 1 raw material for food.', user_id='test1234'):
    events.append(chunk)

print("Number of events:", len(events))
for e in events:
    print(e)
