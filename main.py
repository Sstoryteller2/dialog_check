#!/usr/bin/env python3
# coding: utf-8

import pandas as pd
import functions

df=pd.read_csv('test_data.csv') 
dlg_ids=df['dlg_id'].unique().tolist() #собираем все айди диалогов

res_df=functions.get_dlg(df, dlg_ids)
res_df.to_csv('res_data.csv', index=False)
print ('результат сохранён в файл res_data.csv')
