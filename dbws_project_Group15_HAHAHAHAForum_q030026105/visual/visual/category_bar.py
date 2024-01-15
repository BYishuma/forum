import pandas as pd
from pyecharts import options as opts
from pyecharts.charts import PictorialBar
from pyecharts.globals import SymbolType

data = pd.read_csv("cleaned_hm.csv")
x = data[['predicted_category']]

# make it to list
x = x.values.reshape(1,-1).tolist()
words = []
for i in x:
    for u in i:
        words.append(u)
# print(words)

# count the words in the list
d = {}
for i in words:
    if i not in d:
        d[i] = 1
    else:
        d[i] += 1
category = list(d.keys())
count = list(d.values())
print(category)
print(count)


c = (
    PictorialBar()
    .add_xaxis(category)
    .add_yaxis(
        "Category Bar",
        count,
        label_opts=opts.LabelOpts(is_show=False),
        symbol_size=18,
        symbol_repeat="fixed",
        symbol_offset=[0, 0],
        is_symbol_clip=True,
        symbol=SymbolType.RECT,
        color="#ef5b9c"
    )
    .reversal_axis()
    .set_global_opts(
        title_opts=opts.TitleOpts(title="category_bar"),
        xaxis_opts=opts.AxisOpts(is_show=False),
        yaxis_opts=opts.AxisOpts(
            axistick_opts=opts.AxisTickOpts(is_show=False),
            axisline_opts=opts.AxisLineOpts(
                linestyle_opts=opts.LineStyleOpts(opacity=0)
            ),
        ),
    )
    .render("category_bar.html")
)