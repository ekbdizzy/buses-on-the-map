import os
import json
import trio

from sys import stderr
from trio_websocket import open_websocket_url

WEBSOCKET_URL = 'ws://127.0.0.1:8000'


def load_routes(directory_path='routes'):
    for filename in os.listdir(directory_path):
        if filename.endswith(".json"):
            filepath = os.path.join(directory_path, filename)
            with open(filepath, 'r', encoding='utf8') as file:
                yield json.load(file)


async def run_bus(url, bus_id, route, timeout=1):
    try:
        async with open_websocket_url(url) as ws:
            for lat, lng in route:
                message = json.dumps({"busId": bus_id, "lat": lat, "lng": lng, "route": bus_id}, ensure_ascii=False)
                await ws.send_message(message)
                await ws.get_message()
                await trio.sleep(timeout)
    except OSError as ose:
        print('Connection attempt failed: %s' % ose, file=stderr)


async def main():
    async with trio.open_nursery() as nursery:
        counter = 0
        for route in load_routes('routes'):
            if counter > 10:
                break
            nursery.start_soon(run_bus, WEBSOCKET_URL, route["name"], route["coordinates"], )
            counter += 1

trio.run(main)
