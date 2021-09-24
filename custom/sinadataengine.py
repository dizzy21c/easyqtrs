import easyquotation
from datetime import datetime, date
import json
import easyquant
# from easyquant import MongoIo
# from easyquant import DefaultQuotationEngine, DefaultLogHandler, PushBaseEngine
from easyquant import PushBaseEngine
# from custom.fixedmainengine import FixedMainEngine


class SinaEngine(PushBaseEngine):
    # EventType = 'data-sina'
    # PushInterval = 10
    config = None
    codelist = []

    def init(self, idx = False):
        self.source = easyquotation.use('sina')  # sina, tencent/qq
        # self.mongo = MongoIo()
        # self.codelist = list(self.mongo.get_stock_list().index)

    def fetch_quotation(self):
        if self.EventType == "worker":
            return []

        if self.config is None:
            if len(self.codelist) > 0:
                # print("fetch for code list", self.codelist[:5])
                return self.fetch_quotation_codelist()
            else:
                # print("detch for config None")
                return self.fetch_quotation_all()
        else:
            # print("fetch for config")
            return self.fetch_quotation_config()

    def fetch_quotation_all(self):
        out = self.source.market_snapshot(prefix=True) 
        return out

    def fetch_quotation_config(self):
        config_name = './config/%s.json' % self.config
        with open(config_name, 'r') as f:
            data = json.load(f)
            out = self.source.stocks(data['code'])
            while len(out) == 0:
                out = self.source.stocks(data['code'])
            return out

    def fetch_quotation_codelist(self):
        out = self.source.stocks(self.codelist)
        while len(out) == 0:
            # print("fetch-quotation-codelist 4 while")
            out = self.source.stocks(self.codelist)
        return out
            
