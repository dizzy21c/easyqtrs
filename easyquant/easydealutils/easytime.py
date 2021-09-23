import datetime
import doctest
from functools import lru_cache

import requests
import math

class EasyTime(object):
    def __init__(self):
        pass
    
    def _is_holiday(self, day):
        # 该接口可能将于 2016.7.1 过期, 请关注该主页
        api = 'http://www.easybots.cn/api/holiday.php'
        params = {'d': day}
        rep = requests.get(api, params)
        res = rep.json()[day if isinstance(day, str) else day[0]]
        return True if res == "1" else False


    def is_holiday(self, now_time):
        today = now_time.strftime('%Y%m%d')
        # return _is_holiday(today)
        return False


    def is_weekend(self, now_time):
        return now_time.weekday() >= 5


    def is_trade_date(self, now_time):
        return not (self.is_holiday(now_time) or self.is_weekend(now_time))


    def get_next_trade_date(self, now_time):
        """
        :param now_time: datetime.datetime
        :return:
        >>> import datetime
        >>> get_next_trade_date(datetime.date(2016, 5, 5))
        datetime.date(2016, 5, 6)
        """
        now = now_time
        max_days = 365
        days = 0
        while 1:
            days += 1
            now += datetime.timedelta(days=1)
            if self.is_trade_date(now):
                if isinstance(now, datetime.date):
                    return now
                else:
                    return now.date()
            if days > max_days:
                raise ValueError('无法确定 %s 下一个交易日' % now_time)


    OPEN_TIME = (
        (datetime.time(9, 15, 0), datetime.time(11, 30, 0)),
        (datetime.time(13, 0, 0), datetime.time(15, 0, 0)),
    )


    def is_tradetime(self, now_time):
        """
        :param now_time: datetime.time()
        :return:
        """
        now = now_time.time()
        for begin, end in self.OPEN_TIME:
            if begin <= now < end:
                return True
        else:
            return False


    PAUSE_TIME = (
        (datetime.time(11, 30, 0), datetime.time(12, 59, 30)),
    )


    def is_pause(self, now_time):
        """
        :param now_time:
        :return:
        """
        now = now_time.time()
        for b, e in self.PAUSE_TIME:
            if b <= now < e:
                return True


    CONTINUE_TIME = (
        (datetime.time(12, 59, 30), datetime.time(13, 0, 0)),
    )

    def get_begin_trade_date(self, minute = 1):
        ts_now = datetime.datetime.now()
        return datetime.datetime(ts_now.year, ts_now.month, ts_now.day, 9, 30)

    def get_minute_date(self, minute = 1, ts_now = datetime.datetime.now()):
        delta = 0
        csec = ts_now.second
        ts_hour=ts_now.hour
        if csec > 2:
            if math.ceil(ts_now.minute / minute) == ts_now.minute / minute:
                delta = 1
        nm = (math.ceil(ts_now.minute / minute) + delta) * minute
        if nm > 59:
            nm = nm - 60
            ts_hour = ts_hour + 1
        return datetime.datetime(ts_now.year, ts_now.month, ts_now.day, ts_hour, nm)

    def get_minute_date_str(self, str_date, minute = 1):
        ts_now = datetime.datetime.strptime(str_date, '%Y-%m-%d %H:%M:%S')
        # nm = int(ts_now.minute / minute) * minute
        # return datetime.datetime(ts_now.year, ts_now.month, ts_now.day, ts_now.hour, nm)
        return self.get_minute_date(ts_now=ts_now, minute=minute)

    def is_continue(self, now_time):
        now = now_time.time()
        for b, e in self.CONTINUE_TIME:
            if b <= now < e:
                return True
        return False


    CLOSE_TIME = (
        datetime.time(15, 0, 0),
    )


    def is_closing(self, now_time, start=datetime.time(14, 54, 30)):
        now = now_time.time()
        for close in CLOSE_TIME:
            if start <= now < close:
                return True
        return False

if __name__ == "__main__":
    doctest.testmod()