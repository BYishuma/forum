import pandas as pd
from pyecharts import options as opts
from pyecharts.charts import Bar

data = pd.read_csv("demographic.csv")
x = data[['age']]


# make it to list
x = x.values.reshape(1,-1).tolist()
age = []
for i in x:
    for u in i:
        age.append(u)
for w in age:
    try:
        w = int(w)
    except:
        age.remove(w)  # remove the incorrect ages

# print(age)
age = list(map(int, age))  # change the elements inside words to int
age = sorted(age)  # sorted by increasing value


# count the elements in the list
d = {}
for i in age:
    if i not in d:
        d[i] = 1
    else:
        d[i] += 1

age = list(d.keys())
count = list(d.values())
print(age)
print(count)

c = (
    Bar()
    .add_xaxis(age)
    .add_yaxis("Age", count, color="#444693")
    .set_global_opts(
        title_opts=opts.TitleOpts(title="age_bar"),
        datazoom_opts=[opts.DataZoomOpts(), opts.DataZoomOpts(type_="inside")],
    )
    .render("age_bar.html")
)