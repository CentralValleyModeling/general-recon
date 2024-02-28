# summary_table.py
# Make Summary Table from dataframe

def make_summary_df(df,var_dict,start_yr=1922,end_yr=2021):
    #start_yr = 1922
    #end_yr = 2021
    monthfilter = [1,2,3,4,5,6,7,8,9,10,11,12]
    df1 = df.loc[(df['icm'].isin(monthfilter)) &
                (df['iwy']>=start_yr) &(df['iwy']<=end_yr)
                ] 

    # Do Conversions
    for var in var_dict:
        b = (var_dict[var]['bpart'])
        if var_dict[var]['table_convert']=='cfs_taf':
            print(f'converted {b} to TAF')
            df1[b]=df1[b]*df1['cfs_taf']
        else:
            print(var_dict[var]['pathname'])

    # Annual Average
    df_tbl = round(df1.groupby(["Scenario"]).sum()/(end_yr-start_yr+1))

    # Drop the index columns
    df_tbl.drop(['icy','icm','iwy','iwm','cfs_taf'],axis=1,inplace=True)

    df_tbl = df_tbl.T
    df_tbl['diff']=df_tbl['Orov_Sens']-df_tbl['Baseline']
    df_tbl['perdiff'] = round((df_tbl['Orov_Sens']-df_tbl['Baseline'])/df_tbl['Baseline'],2)*100
    df_tbl.reset_index(inplace=True)
    return df_tbl

