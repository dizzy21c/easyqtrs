import pandas as pd
class DataUtil:
    def __init__ (self):
        pass

    def series(self, data):
        pd.Series({'close':data['close'], 'open':data['open'], 'low':data['low'], 'high':data['high'], 'vol':data['vol']})

    def append2series(self, src, data):
        if len(src['D']) == 0:
            return ([],[],[],[],[],[])

        ldata = data['date']
        # if list(df['date'])[-1] == ldata:
            # return
        D = self.addSeries(src['D'], data['date'])
        H = self.addSeries(src['H'], data['high'])
        L = self.addSeries(src['L'], data['low'])
        C = self.addSeries(src['C'], data['close'])
        O = self.addSeries(src['O'], data['open'])
        V = self.addSeries(src['V'], data['volume'])
        # # D = self.psd.append(Series([data['date']], index=[self.dsize])) 
        # if src.pre_c == 0:
        #     pct = 0
        # else:
        #     pct = (C[src.dsize] - src.pre_c ) * 100 / src.pre_c

        return (C,H,L,O,V,D)
        # return {'C':C, 'H':psh, 'L':psl, 'O':pso, 'V':psv, 'D':psd}

    def addSeries(self, ps_src, new_value):
        psize = len(ps_src)
        return ps_src.append(pd.Series([new_value], index=[psize])) 


    def df2series(self, data_df):
        if data_df is None:
            psc = pd.Series()
            psh = pd.Series()
            psl = pd.Series()
            pso = pd.Series()
            psv = pd.Series()
            psd = pd.Series()
        else:
            psc = data_df.close # rlist['close']
            psh = data_df['high']
            psl = data_df['low']
            pso = data_df['open']
            psv = data_df['volume']
            psd = data_df['date']

        # return {'c':psc, 'h':psh, 'l':psl, 'o':pso, 'v':psv, 'd':psd, 'pc':pre_c}
        return {'C':psc, 'H':psh, 'L':psl, 'O':pso, 'V':psv, 'D':psd}


    def day_summary(self, data, rtn={}):
        pc = data['close']
        c = data['now'] 
        if c == 0 or pc == 0:
            return rtn

        pct = (c - pc) * 100 / pc
        if rtn == {}:
            rtn['utop'] = 0
            rtn['dtop'] = 0

            rtn['u6-9'] = 0
            rtn['u3-6'] = 0
            rtn['u0-3'] = 0

            rtn['d0-3'] = 0
            rtn['d3-6'] = 0
            rtn['d6-9'] = 0

            rtn['up'] = 0
            rtn['down'] = 0

            if pct < 0:
                rtn['down'] = rtn['down'] + 1
            else:
                rtn['up'] = rtn['up'] + 1

            if pct >= 0 and pct < 3:
                rtn['u0-3'] = rtn['u0-3'] + 1

            if pct >= 3 and pct < 6:
                rtn['u3-6'] = rtn['u3-6'] + 1

            if pct >= 6 and pct <= 9.9:
                rtn['u6-9'] = rtn['u6-9'] + 1

            if pct > 9.9 and pct < 50:
                rtn['utop'] = rtn['utop'] + 1

            if pct < 0 and pct > -3:
                rtn['d0-3'] = rtn['d0-3'] + 1

            if pct <= -3 and pct > -6:
                rtn['d3-6'] = rtn['d3-6'] + 1

            if pct <= -6 and pct >= -9.9:
                rtn['d6-9'] = rtn['d6-9'] + 1

            if pct < -9.9:
                rtn['dtop'] = rtn['dtop'] + 1
        else:
            if pct < 0:
                rtn['down'] = rtn['down'] + 1
            else:
                rtn['up'] = rtn['up'] + 1

            if pct >= 0 and pct < 3:
                rtn['u0-3'] = rtn['u0-3'] + 1

            if pct >= 3 and pct < 6:
                rtn['u3-6'] = rtn['u3-6'] + 1

            if pct >= 6 and pct <= 9.9:
                rtn['u6-9'] = rtn['u6-9'] + 1

            if pct > 9.9 and pct < 50:
                rtn['utop'] = rtn['utop'] + 1

            if pct < 0 and pct > -3:
                rtn['d0-3'] = rtn['d0-3'] + 1

            if pct <= -3 and pct > -6:
                rtn['d3-6'] = rtn['d3-6'] + 1

            if pct <= -6 and pct >= -9.9:
                rtn['d6-9'] = rtn['d6-9'] + 1

            if pct < -9.9:
                rtn['dtop'] = rtn['dtop'] + 1

        return rtn
