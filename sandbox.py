#from html_report import load_data_mult
from collections import namedtuple
import pandas as pd
import yaml
#load_data_mult()

with open('dictionary.yaml', 'r') as file:
    var_dict = yaml.safe_load(file)

for var in var_dict:
    print(var_dict[var]['bpart'])

paths = [
        # Storage
        "/CALSIM/S_OROVL/STORAGE//.*/.*/;",
        "/CALSIM/S_FOLSM/STORAGE//.*/.*/;",
        "/CALSIM/S_SHSTA/STORAGE//.*/.*/;",            
        "/CALSIM/S_TRNTY/STORAGE//.*/.*/;",            
        "/CALSIM/S_SLUIS_SWP/STORAGE//.*/.*/;",
        "/CALSIM/S_SLUIS_CVP/STORAGE//.*/.*/;",
        # River Flows
        "/CALSIM/C_LWSTN/.*//.*/.*/;1",
        "/CALSIM/D_LWSTN_CCT011/.*//.*/.*/;1",
        "/CALSIM/C_WKYTN/.*//.*/.*/;1",
        "/CALSIM/C_KSWCK/.*//.*/.*/;1",
        "/CALSIM/C_SAC097/.*//.*/.*/;1",
        "/CALSIM/C_FTR059/.*//.*/.*/;1",
        "/CALSIM/C_FTR003/.*//.*/.*/;1",
        "/CALSIM/C_YUB006/.*//.*/.*/;1",
        "/CALSIM/C_SAC083/.*//.*/.*/;1",
        "/CALSIM/C_NTOMA/.*//.*/.*/;1",
        "/CALSIM/C_AMR004/.*//.*/.*/;1",
        "/CALSIM/GP_SACWBA/.*//.*/.*/;1",
        #Exports
        "/CALSIM/C_CAA003/.*//.*/.*/;1",
        "/CALSIM/C_CAA003_SWP/.*//.*/.*/;1",
        "/CALSIM/C_CAA003_CVP/.*//.*/.*/;1",
        "/CALSIM/C_CAA003_WTS/.*//.*/.*/;1",
        "/CALSIM/C_DMC000/.*//.*/.*/;1",
        "/CALSIM/C_DMC000_CVP/.*//.*/.*/;1",
        "/CALSIM/C_DMC000_WTS/.*//.*/.*/;1",
        #Deliveries
        "/CALSIM/SWP_TA_TOTAL/.*//.*/.*/;1",
        "/CALSIM/SWP_IN_TOTAL/.*//.*/.*/;1",
        "/CALSIM/SWP_CO_TOTAL/.*//.*/.*/;1",
        ]

bparts = []
for path in paths:
    bparts.append(path.split('/')[2])

df = pd.DataFrame()
df = pd.read_csv('temp_mult.csv', index_col=0, parse_dates=True)

# Make Summary Table from dataframe
# Filters
start_yr = 1922
end_yr = 2021
monthfilter = [1,2,3,4,5,6,7,8,9,10,11,12]
#monthfilter = [9]
df1 = df.loc[(df['icm'].isin(monthfilter)) &
             (df['iwy']>=start_yr) &(df['iwy']<=end_yr)
            ] 

for path in paths:
    #print(path)
    #print(path.split(';')[1])
    #print(path.split(';')[1]==str(1))
    if path.split(';')[1]==str(1):
        #print(path)
        df1[path.split('/')[2]]=df1[path.split('/')[2]]*df1['cfs_taf']
    else:
        continue
        #print(path)

df_tbl = round(df1.groupby(["Scenario"]).sum()/(end_yr-start_yr+1))
df_tbl.drop(['icy','icm','iwy','iwm','cfs_taf'],axis=1,inplace=True)
df_tbl = df_tbl.T
df_tbl['diff']=df_tbl['Orov_Sens']-df_tbl['Baseline']
df_tbl['perdiff'] = (df_tbl['Orov_Sens']-df_tbl['Baseline'])/df_tbl['Baseline']
df_tbl.reset_index(inplace=True)
#print(df_tbl)
