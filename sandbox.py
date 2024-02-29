#from html_report import load_data_mult
from collections import namedtuple
import pandas as pd
import yaml

import pandas as pd
import matplotlib.pyplot as plt

# Assuming df is your DataFrame
# Replace df with the name of your DataFrame

# Create a sample DataFrame
data = {'A': [3, 6, 2],
        'B': [9, 1, 5],
        'C': [4, 7, 8]}
df = pd.DataFrame(data)

# Rank the DataFrame
ranked_df = df.rank(axis=0)

# Plot the ranked DataFrame
ranked_df.plot(kind='bar')
plt.title('Ranked DataFrame')
plt.xlabel('Index')
plt.ylabel('Rank')
plt.show()