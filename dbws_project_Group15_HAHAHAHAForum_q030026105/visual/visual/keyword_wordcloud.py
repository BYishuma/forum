from pyecharts import options as opts
import pandas as pd
import numpy as np
from pyecharts.charts import WordCloud
from pyecharts.globals import SymbolType

data = pd.read_csv("cleaned_hm.csv")
x = data[['cleaned_hm']]

# reform the dataframe and make it into a text
x = x.values.reshape(1,-1)
s = ''
for i in x:
    for j in i:
        for g in j:
            s=s+g
s = s.lower()
for ch in '+[]%=`<>|,.?!/"\';:-_$~()&1234567890^*':
    s = s.replace(ch, " ")
words = s.split()  # split the text to words

# delete some useless words
object_words = []
useless_words = pd.read_csv("useless.csv").values
for w in words:
    if w not in useless_words:
        object_words.append(w)
# print(object_words)

# the objected list of the top 49 hot words
d = {}
for i in object_words:
    if i not in d:
        d[i] = 1
    else:
        d[i] += 1
d = sorted(d.items(), key = lambda x:x[1], reverse = True)
d = d[0:50]
print(d)


c = (
    WordCloud()
    .add("", d, word_size_range = [30, 120], word_gap = 35, shape = "pentagon")
    .set_global_opts(title_opts=opts.TitleOpts(title="keyword_wordcloud"))
    .render("keyword_wordcloud.html")
)














