import datetime as dt
from threading import Thread

code = ['fu2006', 'sc2109', 'sc2106', 'sc2006', 'CF007', 'TA007', 'ag2103', 'al2103', 'au2104', 'bu2203', 'cu2103',
        'hc2103', 'ni2103', 'pb2103', 'rb2103', 'ru2103', 'sn2103', 'sp2103', 'wr2103', 'zn2103', 'PM103', 'RI103',
        'RM103', 'SF103', 'SM103', 'WH103', 'a2103', 'b2103', 'bb2103', 'c2103', 'cs2103', 'fb2103', 'i2103', 'j2103',
        'jm2103', 'l2103', 'm2103', 'p2103', 'pp2103', 'v2103', 'y2103', 'l2008', 'm2008', 'p2008', 'pp2008', 'v2008',
        'y2008', 'CY008', 'FG008', 'MA008', 'RM008', 'RS008', 'SF008', 'SM008', 'IC2012', 'IF2012', 'IH2012', 'fu2103',
        'sc2303', 'fu2101', 'sc2101', 'sc2102', 'fu2102', 'ZC104', 'ZC102', 'ag2102', 'al2102', 'au2005', 'bu2008',
        'cu2102', 'hc2102', 'ni2102', 'pb2102', 'rb2102', 'sn2102', 'sp2102', 'wr2102', 'zn2102', 'ZC103', 'IC2005',
        'IF2005', 'IH2005', 'TA104', 'SM104', 'ag2104', 'al2104', 'au2007', 'bu2010', 'cu2104', 'hc2104', 'ni2104',
        'pb2104', 'rb2104', 'ru2104', 'sn2104', 'sp2104', 'wr2104', 'zn2104', 'b2104', 'bb2104', 'fb2104', 'CY104',
        'FG104', 'i2104', 'j2104', 'jm2104', 'l2104', 'p2104', 'pp2104', 'v2104', 'MA104', 'SF104', 'LR011', 'CF101',
        'TA101', 'SR101', 'ag2101', 'al2101', 'au2102', 'bu2007', 'cu2101', 'hc2101', 'ni2101', 'pb2101', 'rb2101',
        'ru2101', 'sn2101', 'sp2101', 'wr2101', 'zn2101', 'AP101', 'CY101', 'FG101', 'JR101', 'LR101', 'MA101',
        'OI101', 'PM101', 'RI101', 'RM101', 'SF101', 'SM101', 'IC2009', 'IF2009', 'IH2009', 'WH101', 'a2101', 'b2101',
        'bb2101', 'c2101', 'cs2101', 'fb2101', 'i2101', 'j2101', 'jm2101', 'l2101', 'm2101', 'p2101', 'pp2101',
        'v2101', 'y2101', 'fu2104', 'sc2104', 'eg2101', 'jd2101', 'eg2102', 'jd2102', 'eg2009', 'jd2009', 'i2010',
        'j2010', 'jm2010', 'l2010', 'p2010', 'pp2010', 'v2010', 'eg2010', 'jd2010', 'fu2011', 'sc2011', 'ag2011',
        'al2011', 'au2012', 'bu2005', 'cu2011', 'hc2011', 'ni2011', 'pb2011', 'CF005', 'TA005', 'SR005', 'a2005',
        'AP005', 'CY005', 'FG005', 'JR005', 'LR005', 'MA005', 'OI005', 'PM005', 'RI005', 'RM005', 'SF005', 'b2005',
        'bb2005', 'c2005', 'cs2005', 'fb2005', 'i2005', 'SM005', 'WH005', 'j2005', 'jm2005', 'l2005', 'eg2103',
        'jd2103', 'eg2004', 'jd2004', 'fu2005', 'ag2010', 'al2010', 'cu2010', 'hc2010', 'ni2010', 'pb2010', 'rb2010',
        'ru2010', 'sn2010', 'sp2010', 'wr2010', 'zn2010', 'rb2011', 'ru2011', 'sn2011', 'sp2011', 'wr2011', 'zn2011',
        'ZC101', 'TA102', 'CY102', 'FG102', 'MA102', 'SF102', 'SM102', 'b2102', 'bb2102', 'fb2102', 'i2102', 'j2102',
        'jm2102', 'l2102', 'p2102', 'pp2102', 'v2102', 'CF103', 'TA103', 'SR103', 'T2012', 'TF2012', 'TS2012', 'AP103',
        'CY103', 'FG103', 'JR103', 'LR103', 'MA103', 'OI103', 'ag2012', 'al2012', 'bu2112', 'cu2012', 'hc2012',
        'ni2012', 'pb2012', 'rb2012', 'sn2012', 'sp2012', 'wr2012', 'zn2012', 'm2005', 'p2005', 'pp2005', 'v2005',
        'y2005', 'ZC007', 'TA008', 'b2008', 'bb2008', 'fb2008', 'i2008', 'j2008', 'jm2008', 'm2007', 'p2007', 'pp2007',
        'v2007', 'y2007', 'eg2007', 'jd2007', 'fu2008', 'sc2008', 'ZC008', 'ZC009', 'ZC011', 'eg2011', 'jd2011',
        'fu2012', 'sc2212', 'TA012', 'b2012', 'bb2012', 'fb2012', 'i2012', 'bu2009', 'j2012', 'jm2012', 'l2012',
        'm2012', 'p2012', 'pp2012', 'bu2006', 'ag2007', 'al2007', 'au2008', 'cu2007', 'hc2007', 'ni2007', 'pb2007',
        'rb2007', 'ru2007', 'sn2007', 'sp2007', 'wr2007', 'zn2007', 'sc2007', 'v2012', 'y2012', 'T2009', 'TF2009',
        'TS2009', 'AP012', 'CY012', 'FG012', 'MA012', 'SF012', 'SM012', 'OI009', 'fu2007', 'PM009', 'RI009', 'RM009',
        'RS009', 'SF009', 'ZC006', 'sc2209', 'fu2009', 'CF011', 'TA011', 'SR011', 'SR009', 'CF009', 'TA009', 'SM009',
        'WH009', 'ag2009', 'al2009', 'au2010', 'bu2109', 'cu2009', 'hc2009', 'ni2009', 'pb2009', 'rb2009', 'ru2009',
        'sn2009', 'bu2103', 'ZC010', 'RM011', 'RS011', 'SF011', 'SM011', 'al2006', 'bu2106', 'cu2006', 'hc2006',
        'ni2006', 'pb2006', 'rb2006', 'ru2006', 'sn2006', 'sp2006', 'wr2006', 'zn2006', 'CY006', 'FG006', 'MA006',
        'SF006', 'SM006', 'b2006', 'bb2006', 'fb2006', 'i2006', 'j2006', 'jm2006', 'l2006', 'ZC005', 'eg2006',
        'jd2006', 'SR007', 'sc2103', 'sc2112', 'sc2009', 'AP011', 'CY011', 'ag2005', 'al2005', 'au2006', 'cu2005',
        'hc2005', 'ni2005', 'pb2005', 'rb2005', 'ru2005', 'sn2005', 'sp2005', 'wr2005', 'zn2005', 'FG011', 'JR011',
        'MA011', 'OI011', 'PM011', 'RI011', 'WH011', 'a2011', 'b2011', 'bb2011', 'c2011', 'cs2011', 'fb2011', 'i2011',
        'j2011', 'jm2011', 'l2011', 'm2011', 'p2011', 'pp2011', 'v2011', 'y2011', 'ZC012', 'TA006', 'pp2006', 'v2006',
        'ag2006', 'p2006', 'eg2008', 'jd2008', 'sc2010', 'fu2010', 'IC2006', 'IF2006', 'IH2006', 'TA010', 'AP010',
        'CY010', 'FG010', 'MA010', 'SF010', 'SM010', 'b2010', 'bb2010', 'fb2010', 'sp2009', 'wr2009', 'zn2009',
        'a2009', 'b2009', 'bb2009', 'c2009', 'cs2009', 'eg2012', 'jd2012', 'eg2005', 'jd2005', 'fb2009', 'i2009',
        'j2009', 'jm2009', 'l2009', 'm2009', 'p2009', 'pp2009', 'v2009', 'y2009', 'T2006', 'TF2006', 'TS2006', 'CY009',
        'FG009', 'JR009', 'MA009', 'bu2012', 'sc2206', 'sc2203', 'sc2012', 'sc2005', 'AP007', 'CY007', 'FG007',
        'JR007', 'LR007', 'MA007', 'OI007', 'PM007', 'RI007', 'RM007', 'RS007', 'SF007', 'SM007', 'WH007', 'a2007',
        'b2007', 'bb2007', 'c2007', 'cs2007', 'fb2007', 'i2007', 'j2007', 'jm2007', 'l2007', 'ag2008', 'al2008',
        'cu2008', 'hc2008', 'ni2008', 'pb2008', 'rb2008', 'ru2008', 'sn2008', 'sp2008', 'wr2008', 'zn2008']
# !/usr/bin/env python3
"""websocket cmd client for wssrv.py example."""
import asyncio
import sys
import aiohttp


class Connector:

    def __init__(self, loop=None, ping_interval=0):
        self.loop = loop or asyncio.get_event_loop()
        self.ws_conn = None
        self.ping_interval = ping_interval or 10
        self.loop.create_task(self._send_message())
        self.subscribe = False
        self.codes = {"resample": ["rb2010"], "real": ["000001"]}
        # self.url = "ws://127.0.0.1:10115/ws/"
        self.url = "ws://quantaxis.tech:10115/ws/"

    async def _connect(self):
        """连接 wss，成功后持续收取消息"""
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=15)) as session:
            async with session.ws_connect(self.url) as conn:
                self.ws_conn = conn
                while True:
                    message = await self.ws_conn.receive(timeout=20)
                    await self._process_raw_message(message)
                    if self.ws_conn.closed:
                        sys.exit("websocket断开连接")

    @property
    def time_now(self):
        return dt.datetime.now()

    @property
    def conn_available(self):
        return self.ws_conn is not None and self.ws_conn.closed is False

    async def _process_raw_message(self, message):
        # print(f"{self.time_now} receive message. type: {message.type}, content: {message.data}")
        """ """
    async def _send_message(self):
        """在 wss 连接上时，定时发送消息；当 wss 断开时，则休眠"""
        while True:
            if self.conn_available and not self.subscribe:
                payload = dict(topic="auth", key="000000000")
                await self.ws_conn.send_json(payload)
                for x in self.codes["real"]:
                    await self.ws_conn.send_json({"topic": "realtime_sub", "room": f"{x}$*$1min"})
                for x in self.codes["resample"]:
                    await self.ws_conn.send_json({"topic": "realtime_sub", "room": x})
                self.subscribe = True
            else:
                await asyncio.sleep(1)

    def start_listening(self):
        """开始连接和监听消息"""
        self.loop.create_task(self._connect())
        self.loop.run_forever()


def crete_app():
    loop = asyncio.new_event_loop()
    a = Connector(loop=loop, ping_interval=2)
    try:
        a.start_listening()
    except KeyboardInterrupt:
        exit()


if __name__ == '__main__':
    threads = []
    thread_limit_count = 500
    for i in range(thread_limit_count):
        p = Thread(target=crete_app)
        p.start()
        threads.append(p)

    for i in threads:
        i.join()
