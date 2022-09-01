import spacy
import numpy as np
import pandas as pd
import difflib
import synonyms

nlp = spacy.load("ru_core_news_lg")

# Позроверка поздаровался ли
def is_greet_in_phrase(text):
    doc=nlp(text)
    greet_list=synonyms.greet_list  
    for token in doc:
        if token.lemma_ in greet_list and (token.dep_ == "amod" or token.dep_ == "ROOT"):       
            return True        
    return False

# Проверка представился ли
def is_introduce_in_phrase(doc):
    intriduce_list=synonyms.intriduce_list
    for token in doc:           
        # Проверяем на наличие именнованной сущиности Person, смотрим отношение nsubj к главному слову из списка для фраз "меня зовут", "моё имя", "с вами говорит", на всякий случай проверяем по леммам
        if token.ent_type_ == 'PER' and token.head.lemma_ in intriduce_list:           
            return True, token.text
        elif token.lemma_ == 'это' and token.dep_ == 'nsubj' and token.head.dep_ == "ROOT":
            return True, token.head.text
    return False

# Получаем название компании 
def similarity(s1, s2):
    normalized1 = s1.lower()
    normalized2 = s2.lower()
    matcher = difflib.SequenceMatcher(None, normalized1, normalized2)
    return matcher.ratio()

def get_company_name(doc):
    company_list=synonyms.company_list
    for i, token in enumerate(doc):        
        count=i    
        if token.lemma_ == "компания":
            company_name_list=list()
            for c, item in enumerate(company_list):
                company_name_list.append(similarity(doc[count+1].text, item))                
            company_index=(company_name_list.index(max(company_name_list)))
            if max(company_name_list) < 0.6:
                company_name=doc[count+1].text             
            else:             
                company_name=company_list[company_index]
            return True, company_name
    return False

#проверка прощания
def is_bye(doc):
    byes_list=synonyms.byes_list
    for token in doc:           
        if token.lemma_ in byes_list[0] or (token.lemma_ in byes_list[1] and token.dep_ =='case'):            
            return True
    return False

# проход по фразам
def find_items(df, dlg_len, item, function):
    if dlg_len < 0:
        i=-1 
        while i > dlg_len:                                                            
            text=df.loc[(df["role"]=="manager") & (df['dlg_id']==item)].iloc[i][3]                      
            doc=nlp(text)            
            if function(doc):
                index=df.loc[(df["role"]=="manager") & (df['dlg_id']==item)].iloc[i].name
                return function(doc), index
            i-=1
            if i == dlg_len:
                return False
    else:        
        for i in range(dlg_len):
            text=df.loc[(df["role"]=="manager") & (df['dlg_id']==item)].iloc[i][3]        
            doc=nlp(text)
            if function(doc):
                index=df.loc[(df["role"]=="manager") & (df['dlg_id']==item)].iloc[i].name
                return function(doc), index
    return function(doc)

#получаем информацию
def get_dlg(df, dlg_ids):  
    
    df["insight"]=0
    for i in range(6):    
        df[chr(97+i)]=0
        i+=1
        
    for c, item in enumerate(dlg_ids):
        dlg_len=len(df.loc[(df["role"]=="manager") & (df['dlg_id']==item)])     
        #ожидаем представление и приветвие в первых трёх фразах        
        greet=find_items(df, 3, item, is_greet_in_phrase)
        intro=find_items(df, 3, item, is_introduce_in_phrase)
        company=find_items(df, 3, item, get_company_name)
        bye=find_items(df, -4, item, is_bye)
        
        insight_txt=""
        intro_n_comp=""        
      
        if greet:                
            df["insight"].iloc[greet[1]]="greeting=True"
            insight_txt+="greeting=True, "
            df["a"].iloc[greet[1]]="greeting=True"            
        if not greet:
            index=df.loc[(df["role"]=="manager") & (df['dlg_id']==item)].iloc[0].name #первая фраза менеджена
            df["insight"].iloc[index]="greeting=False"
            insight_txt+="greeting=False, "            
            df["a"].iloc[index]="greeting=False"            
        
        if intro:            
            df["insight"].iloc[intro[1]]="introduction=True"
            df["b"].iloc[intro[1]]="introduction=True"
            df["c"].iloc[intro[1]]=intro[0][1]
            intro_n_comp+="introduction=True, "
            insight_txt+="introduction=True, "
        if not intro:           
            intro_n_comp+="introduction=False "            

        if company:            
            intro_n_comp+="company=True"
            df["insight"].iloc[company[1]]=intro_n_comp
            insight_txt+="company=True, "
            df["d"].iloc[company[1]]=company[0][1]
        if not company:
            insight_txt+="company=False, "            

        if bye:            
            insight_txt+="bying=True"            
            df["insight"].iloc[bye[1]]="bye=True"
            df["e"].iloc[bye[1]]="bye=True"            
        if not bye:
            insight_txt+="bying=False"
        
        index=df.loc[(df["role"]=="manager") & (df['dlg_id']==item)].iloc[0].name #первая фраза менеджена
        index=df.loc[(df['dlg_id']==item)].iloc[0].name
        df["insight"].iloc[index]=insight_txt
        
        if greet and bye:
            df["f"].iloc[bye[1]]="greet-bye=True"           
        else:
            df["f"].iloc[0]="greet-bye=False"
    return df
