import pandas as pd
from pycnnum import cn2num

df_a = pd.read_csv('lvr_landcsv/a_lvr_land_a.csv').iloc[1:, :]
df_b = pd.read_csv('lvr_landcsv/b_lvr_land_a.csv').iloc[1:, :]
df_e = pd.read_csv('lvr_landcsv/e_lvr_land_a.csv').iloc[1:, :]
df_f = pd.read_csv('lvr_landcsv/f_lvr_land_a.csv').iloc[1:, :]
df_h = pd.read_csv('lvr_landcsv/h_lvr_land_a.csv').iloc[1:, :]

df_all = pd.concat([df_a, df_b, df_e, df_f, df_h])
df_all = df_all.reset_index(drop=True)

df_all['總樓層數_num'] = df_all['總樓層數'].str.split('層').str[0].apply(lambda x: cn2num(x) if type(x)==str else x)

df_filter_a = df_all.loc[(df_all['主要用途']=='住家用') & (df_all['建物型態']=='住宅大樓(11層含以上有電梯)') & (df_all['總樓層數_num'] >= 13)]
df_filter_a.to_csv('filter_a.csv', index=False)

df_all['車位數'] = df_all['交易筆棟數'].str.split('車位').str.get(1)
df_filter_b = pd.DataFrame({
    '總件數': df_all.count()['總價元'], 
    '總車位數': df_all['車位數'].astype(int).sum(), 
    '平均總價元': df_all['總價元'].astype(int).sum()/df_all.count()['總價元'], 
    '平均車位總價元': df_all['車位總價元'].astype(int).sum()/df_all['車位數'].astype(int).sum()
    },index=[0]
)
df_filter_b.to_csv('filter_b.csv', index=False)