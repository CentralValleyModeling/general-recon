import pandas as pd
import pandss as pdss


monthfilter = [1,2,3,4,5,6,7,8,9,10,11,12]
month_map = {'Jan':1,'Feb':2,'Mar':3, 'Apr':4,
            'May':5,'Jun':6,'Jul':7, 'Aug':8,
            'Sep':9,'Oct':10,'Nov':11, 'Dec':12,}

def load_data_mult(scenarios, var_dict):
    """
    # Load data from the selected DSS files into a .csv
    """
    dfi = pd.DataFrame()
    df = pd.DataFrame()
    appended_data = []

    for scenario in scenarios:
        print(scenario.pathname,scenario.alias)
        with pdss.DSS(scenario.pathname) as dss:
  
            # Loop to read all paths into DataFrame
            for var in var_dict:
                pn = var_dict[var]['pathname']
                path_i = pdss.DatasetPath.from_str(pn)
                print (pn)

                for regular_time_series in dss.read_multiple_rts(path_i):
                    dfi['Scenario'] = scenario.alias
                    dfi[regular_time_series.path.b] = regular_time_series.to_frame()
        
        # Make a list of the DataFrames associated with each DV file
        appended_data.append(dfi)
        dfi = pd.DataFrame()

    # concatenate the individual DataFrames into one big DataFrame
    df = pd.concat(appended_data)
        
    date_map = pd.read_csv('date_map.csv', index_col=0, parse_dates=True)
    df = pd.merge(df,date_map, left_index=True, right_index=True)
    df.to_csv('temp_mult.csv')
    print(df)
    return

def make_ressum_df(df,var_dict,start_yr=1922,end_yr=2021,
                    monthfilter=monthfilter):
        df1 = df.loc[(df['icm'].isin(monthfilter)) &
                (df['iwy']>=start_yr) &(df['iwy']<=end_yr)
                ] 
        
        for i in df1:
            try:
                f = (var_dict[i]['table_display'])
                if f=='wy':
                    df1 = df1.drop(columns=i)
                    
            except KeyError:
                continue
        
        #print(df1)
        df_tbl = round(df1.groupby(["Scenario"]).sum()/(end_yr-start_yr+1))

        # Drop the index columns
        df_tbl.drop(['icy','icm','iwy','iwm','cfs_taf'],axis=1,inplace=True)

        df_tbl = df_tbl.T
        df_tbl['diff']=df_tbl['Orov_Sens']-df_tbl['Baseline']
        df_tbl['perdiff'] = round((df_tbl['Orov_Sens']-df_tbl['Baseline'])/df_tbl['Baseline'],2)*100
        df_tbl.reset_index(inplace=True)
        return df_tbl



def make_summary_df(df,var_dict,start_yr=1922,end_yr=2021,
                    monthfilter=monthfilter):

    df1 = df.loc[(df['icm'].isin(monthfilter)) &
                (df['iwy']>=start_yr) &(df['iwy']<=end_yr)
                ] 
    columns_to_drop = [col for col in df1.columns if 'S_' in col]
    df1 = df1.drop(columns=columns_to_drop)

    # Do Conversions
    for var in var_dict:
        b = (var_dict[var]['bpart'])
        if var_dict[var]['table_convert']=='cfs_taf':
            #print(f'converted {b} to TAF')
            df1[b]=df1[b]*df1['cfs_taf']
        else:
            continue
            #print(var_dict[var]['pathname'])

    # Annual Average
    df_tbl = round(df1.groupby(["Scenario"]).sum()/(end_yr-start_yr+1))

    # Drop the index columns
    df_tbl.drop(['icy','icm','iwy','iwm','cfs_taf'],axis=1,inplace=True)

    df_tbl = df_tbl.T
    df_tbl['diff']=df_tbl['Orov_Sens']-df_tbl['Baseline']
    df_tbl['perdiff'] = round((df_tbl['Orov_Sens']-df_tbl['Baseline'])/df_tbl['Baseline'],2)*100
    df_tbl.reset_index(inplace=True)
    return df_tbl

