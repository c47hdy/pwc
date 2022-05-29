
import pandas as pd
import numpy as np
import re
from datetime import datetime


Example_Data = pd.read_excel(r'C:\Users\Desktop\Python\Example_Data.xlsx',sheet_name='Example_Data',header=1)
Example_DB = pd.read_excel(r'C:\Users\Desktop\Python\Example_Data.xlsx',sheet_name='Example_DB')

Example_Data['key'] = Example_Data['Company ID'].map(str)+Example_Data['Company Name']

#check occurance frequency if 1 then replace with existing name
df = Example_Data.groupby(['Company ID','Company Name']).size().reset_index(name='Freq')
df1 = pd.merge(Example_Data,df,on=(['Company Name','Company ID']))
#if 1 
df1['Company Name'][df1['Freq']==1]=None #(what if only occur once?)
#sort the fill down 
df1 = df1.sort_values(by='Company ID')
df1['Company Name'] = df1[['Company Name']].fillna(method='ffill')

#Fiscal Year Cleaning
df1['Fiscal Year'] = df1['Fiscal Year'].astype(str)
df1['Fiscal Year'] = df1['Fiscal Year'].str.extract(r'(\d{4})',expand=False)
df1 = df1.dropna(subset=['Fiscal Year'])
df1['Fiscal Year'] = df1['Fiscal Year'].astype(int)
df1['Fiscal Year'] = df1['Fiscal Year'].apply(lambda x: x if (x>=1999 and x<=2021) else None)
#df1['Fiscal Year'] = pd.to_datetime(str(df1['Fiscal Year']),format = '%y') #2011 error?


#SIC Cleaning
df1['SIC Code'] = df1['SIC Code'].astype(str)
df1['SIC Code'] = df1['SIC Code'].str.extract(r'(\d{4})',expand=False)
df1 = df1.dropna(subset=['SIC Code'])

#USD GBP filter
df1=df1[df1['Trading Currency'].isin(['USD','GBP'])]

#Integer
df1['SP'] = df1['SP'].fillna(0).astype(int)
df1['CDS'] = df1['CDS'].fillna(0).astype(int)
df1['APD'] = df1['APD'].fillna(0).astype(int)
df1['ARD'] = df1['ARD'].fillna(0).astype(int)
df1['ADA'] = df1['ADA'].fillna(0).astype(int)

#Unpivot table
df2= df1.melt(id_vars=['Company ID','Company Name','Fiscal Year','Industry','SIC Code','Trading Currency'],
         value_vars=['SP','CDS','APD','ARD','ADA'],
         var_name = ['Metric Name'])

df2.rename(columns={'value':'Value1'},inplace=True)
#replace 0
df2['Value1'] = df2['Value1'].apply(lambda x: x if x>0 else np.nan)

#Example_DB.dtypes
#df2.dtypes

#Align dtypes before merge
df2['SIC Code'] = df2['SIC Code'].astype(int)

#Merge two dataframes
df3 = pd.merge(Example_DB,df2,on=(['Company ID','Company Name','Fiscal Year','Industry','SIC Code','Trading Currency','Metric Name']))
df3 = df3.rename(columns={'Value':'Data in DB','Value1':'Data in File'})

#Set condition
conditions=[
    (df3['Data in DB']==0)&(pd.isna(df3['Data in File'])),
    (pd.isna(df3['Data in DB']))&(df3['Data in File']>0),
    (pd.isna(df3['Data in DB']))&(pd.isna(df3['Data in File'])),
    (df3['Data in DB']>0)&(pd.isna(df3['Data in File']))]

values = ["UnEqual","UnEqual","Not_in_DB","Not_in_File"]
df3['ERROR Type'] = np.select(conditions,values,default=None)

#make a copy just in case
df4 = df3.copy()

df4.dropna(subset=['ERROR Type'],inplace=True)
df4 = df4.set_index('Company ID')
print(df4)

#def func(row):
#    if (row['Data in DB'] == '0') & (pd.isna(row['Data in File'])):
#        return 'UnEqual'
#    elif row['Data in DB'] is np.nan and row['Data in File']>0:
#        return 'UnEqual'
#    elif row['Data in DB'] is np.nan and row['Data in File'] is np.nan:
#        return 'Not_in_DB'
#    elif row['Data in DB']>0 and row['Data in File'] is np.nan:
#        return 'Not_in_File'
#    else:
#        return np.nan

#df3['Error Type'] = df3.apply(func,axis=1)
    





