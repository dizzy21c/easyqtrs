#!/usr/bin/env python
#  -*- coding: utf-8 -*-


"""


本代码是基于 https://github.com/shinnytech/websocket-adaptor
"""

import asyncio
import websockets
import sys

loop = asyncio.get_event_loop()


async def handler(addr, fs, fr):
    async with websockets.connect(addr) as websocket:
        loop.create_task(send(websocket, fs))
        while True:
            fr.write(await websocket.recv())


async def send(websocket, fs):
    while True:
        line = fs.readline()
        if not line:
            await asyncio.sleep(0.1)
            continue
        await websocket.send(line)

loop.run_until_complete(handler("ws://127.0.0.1:7890", sys.stdin, sys.stdout))
