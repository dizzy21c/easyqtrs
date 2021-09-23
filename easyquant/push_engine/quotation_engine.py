# coding: utf-8

import easyquotation

from .base_engine import BaseEngine


class DefaultQuotationEngine(BaseEngine):
    """新浪行情推送引擎"""
    EventType = 'quotation'

    def init(self):
        self.source = easyquotation.use('sina')

    def fetch_quotation(self):
        out=self.source.all_market
        if len(out) == 0:
            out = self.source.all_market
        return out
