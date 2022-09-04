#!/usr/bin/env python3
# coding: utf-8

import numpy as np
import functions

arr = np.loadtxt("test_data.csv", delimiter=",", dtype=str, skiprows=1)

#получаем айди диалогов
dlg_ids=np.unique(arr[:,0]).tolist()

#добавляем столбец инсайт
insight= np.zeros((arr.shape[0],1))
arr=np.hstack((arr,insight))

#добавляем столбцы под каждый пункт задания
a_f_cols=np.zeros((arr.shape[0],6))
arr=np.hstack((arr,a_f_cols))

array_head={
    0:"dlg_id",
    1:"line_n",
    2:"role",
    3:"text",
    4:"insight",
    5:"a",
    6:"b",
    7:"c",
    8:"d",
    9:"e",
    10:"f"
}

#получаем индексы фраз менеджера 
manager_phrases_index=list()
for item in dlg_ids:    
    indexes=(np.where((arr[:,2] == "manager") & (arr[:,0]==item)))    
    manager_phrases_index.append(indexes[0])
    
# проходимся по всем диалогам
for c, item in enumerate(dlg_ids):            
    dlg_len = 3 #сколько фраз проверять
    
    phrases, phrase_index = functions.get_phrases(arr, dlg_len, c, manager_phrases_index)  
    
    greet = (functions.chek_phrase(phrases, phrase_index, functions.is_greet_in_phrase))
    intro = (functions.chek_phrase(phrases, phrase_index, functions.is_introduce_in_phrase))
    company = (functions.chek_phrase(phrases, phrase_index, functions.get_company_name))
    dlg_len = -3 #сберем три последние
    
    phrases, phrase_index = functions.get_phrases(arr, dlg_len, c, manager_phrases_index) 
    bye = (functions.chek_phrase(phrases, phrase_index, functions.is_bye))  
    
    insight_txt=""
    intro_n_comp=""
    
    if greet:
        arr[:,4][greet[0]]="greeting=True"
        arr[:,5][greet[0]]="greeting=True"
        insight_txt+="greeting=True, "         
    if not greet:
        ins_index=manager_phrases_index[c][0] #первая фраза менеджера
        arr[:,4][ins_index]="greeting=False"
        arr[:,5][ins_index]="greeting=False"
        insight_txt+="greeting=False, "
        
    if intro:      
        arr[:,4][intro[0]]="introduction=True" 
        arr[:,6][intro[0]]="introduction=True" 
        intro_n_comp+="introduction=True, "
        insight_txt+="introduction=True, "
        arr[:,7][intro[0]]=intro[1][1]        
    if not intro:           
        intro_n_comp+="introduction=False, "
        insight_txt+="introduction=False, " 
        arr[:,6][ins_index]="introduction=False" 
            
    if company:        
        intro_n_comp+="company=True"
        insight_txt+="company=True, "           
        arr[:,4][company[0]]=intro_n_comp
        arr[:,8][company[0]]=company[1][1]
    if not company:
        insight_txt+="company=False, "
        intro_n_comp+="company=False"
            
    if bye:
        arr[:,4][bye[0]]="bying=True"  
        arr[:,9][bye[0]]="bying=True"
        insight_txt+="bying=True"              
    if not bye:
        insight_txt+="bying=False"
        ins_index=np.where(arr[:,0]==item)[0][-1]
        arr[:,4][ins_index]="bying=False" #последняя фраза
        arr[:,9][ins_index]="bying=False"
        
    if greet and bye:
        arr[:,10][greet[0]]="greet-bye=True"         
    else:
        arr[:,10][manager_phrases_index[c][0]]="greet-bye=False"    
        
    
    ins_index=np.where(arr[:,0]==item)[0][0] # индекс первой фразы диалога
    arr[:,4][ins_index]=insight_txt

head=''
for item in array_head.values():
    head+=(item+"; ")
head=head.rstrip("; ")

np.savetxt('res_data.csv', arr, delimiter=';',fmt='%s',  header=head)

print("результат сохранен в файл res_data.csv")
