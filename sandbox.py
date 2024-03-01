#from html_report import load_data_mult
from collections import namedtuple
import pandas as pd
import yaml

import pandas as pd
import matplotlib.pyplot as plt


# Assuming df is your DataFrame with a datetime index
# Replace df with the name of your DataFrame

# Create a sample DataFrame
date_rng = pd.date_range(start='2022-01-01', end='2022-12-31', freq='D')
df = pd.DataFrame(date_rng, columns=['date'])
df['data'] = range(len(df))
df.set_index('date', inplace=True)
print(df)
# Resample the DataFrame by month and calculate the mean for each month
monthly_avg = df.resample('M').mean()

print("Monthly Averages:")
print(monthly_avg)