import pandas as pd
import numpy as np
from pyecharts.charts import Pie
from pyecharts import options as opts

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
    Pie()
    .add(
        "",
        [list(z) for z in zip(category, count)],
        radius = ['30%', '80%'],
        center = ['50%', '50%'],
        rosetype="area"
    )
    .set_global_opts(title_opts=opts.TitleOpts(title="category_pie"))
    .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c}"))
    .render("category_pie.html")
)

