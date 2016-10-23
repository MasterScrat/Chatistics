import matplotlib.pyplot as plt
from ggplot import *
import json
import pprint
import operator
import pandas as pd

a = [1, 1, 2, 1, 1, 4, 5, 6]
histo = {'me': 66583, 'cristi': 9, 'sanglard': 144, 'raph': 4, 'kreshnik': 59, 'phanie': 2, 'damien': 249, 'ralu': 41458, 'brandao': 105, 'johann': 420, 'lionel': 57, 'pascal': 4556, 'delphine': 182, 'nico': 8356, 'dusanter': 26, 'ori': 3682, 'gardiol': 24, 'paul': 347, 'didot': 3, 'silviu': 1010, 'maman': 3816}


df = pd.DataFrame(histo.items(), columns=['name','messages'])

print df
df2 = df.sort_index(by=['messages'])
print df2

p = ggplot(aes(x='name', y='messages'), data=df2) + geom_bar(stat='bar')

print p

exit(0)