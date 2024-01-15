import pandas as pd
import numpy as np
from pyecharts.charts import Pie
from pyecharts import options as opts

data = pd.read_csv("demographic.csv")
x = data[['gender']]

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
gender = list(d.keys())[0:-1]
count = list(d.values())[0:-1]
print(gender)
print(count)

c = (
    Pie()
    .add("", [list(z) for z in zip(['male', 'female', 'optional'], count)])
    .set_global_opts(title_opts=opts.TitleOpts(title="gender_pie"))
    .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c}"))
    .render("gender_pie.html")
)
