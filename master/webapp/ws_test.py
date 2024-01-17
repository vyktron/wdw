import asyncio
import websockets
import pydantic
import json
import os, sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.db import PostgresDB, Location, Dad

loc1 = Location(dad_id=1, latitude=43.3150069, longitude=-0.3793498)

async def send_obj(location: Location):
    async with websockets.connect('ws://localhost:8000/ws') as websocket:
        data = location.model_dump()
        await websocket.send(json.dumps(data))
        response = await websocket.recv()
        print(f"Received response: {response}", flush=True)

# Example usage
asyncio.get_event_loop().run_until_complete(send_obj(loc1))
