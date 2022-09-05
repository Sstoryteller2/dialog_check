#!/usr/bin/env python3
# coding: utf-8

import numpy as np
import functions

if __name__ == "__main__":    
    
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
    
    dlg_len = 3 #сколько фраз проверять

    arr=functions.get_result(arr, dlg_ids, dlg_len, manager_phrases_index)
    
    head=''
    for item in array_head.values():
        head+=(item+"; ")
    head=head.rstrip("; ")

    np.savetxt('res_data.csv', arr, delimiter=';',fmt='%s',  header=head)
    
    print("результат сохранен в файл res_data.csv")