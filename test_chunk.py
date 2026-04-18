import asyncio
import json
from req_gatherer import producer_app

async def test_chunk():
    producer_app.set_up()
    print('Testing what chunks look like...')
    async for chunk in producer_app.stream_query('hi', user_id='test1234'):
        print('CHUNK DICT >>', chunk)
        
asyncio.run(test_chunk())