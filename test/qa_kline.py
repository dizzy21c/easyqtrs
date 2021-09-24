import QUANTAXIS as QA
import pyecharts.options as opts
from pyecharts.charts import Candlestick
from pyecharts.globals import CurrentConfig, NotebookType
CurrentConfig.NOTEBOOK_TYPE = NotebookType.JUPYTER_LAB

code=["000735"]
start_date="2020-01-01"
end_date="2021-01-01"

ax = QA.QA_fetch_stock_day_adv(code,start_date, end_date).data.reset_index(1)
# data = QA.QA_fetch_stock_day_adv(['000001', '000002', '000004', '600000'], '2017-09-01', '2018-05-20')

x_data = ax.index.map(str).values.tolist()
y_data = ax.loc[:,['open',  'close','low','high']].values.tolist()

r =(
    Candlestick(init_opts=opts.InitOpts(width="1440px", height="720px"))
    .add_xaxis(xaxis_data=x_data)
    .add_yaxis(series_name="", y_axis=y_data)
    .set_series_opts()
    .set_global_opts(
        xaxis_opts=opts.AxisOpts(is_scale=True),
        title_opts=opts.TitleOpts(title=code),
    )
)
r.load_javascript()
r.render_notebook()