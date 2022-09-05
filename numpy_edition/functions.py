import spacy
import numpy as np
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

#получаем фарзы которые проверяем на наличие сущностей (dlg_len определяет n - первых и последних)
def get_phrases(arr, dlg_len, c, manager_phrases_index):
    if dlg_len > 0:
        phrases=arr[:,3][manager_phrases_index[c][:dlg_len]] 
        phrase_index=[manager_phrases_index[c][:dlg_len]][0]
        return phrases, phrase_index
    if dlg_len < 0:
        phrases=(arr[:,3][manager_phrases_index[c][dlg_len:]])
        phrase_index=[manager_phrases_index[c][dlg_len:]][0]
        return phrases, phrase_index

#проверяем фразы на наличие сущностей
def chek_phrase(phrases, phrase_index, function):
    for n, phrase in enumerate(phrases):         
        doc=nlp(str(phrase))       
        if function(doc):
            index=phrase_index[n]          
            return(index, function(doc))
    return False

def get_result(arr, dlg_ids, dlg_len, manager_phrases_index):
    # проходимся по всем диалогам
    for c, item in enumerate(dlg_ids):            
        #dlg_len = 3 #сколько фраз проверять

        phrases, phrase_index = get_phrases(arr, dlg_len, c, manager_phrases_index)  

        greet = (chek_phrase(phrases, phrase_index, is_greet_in_phrase))
        intro = (chek_phrase(phrases, phrase_index, is_introduce_in_phrase))
        company = (chek_phrase(phrases, phrase_index, get_company_name))
        dlg_len = (dlg_len*-1) #сберем три последние

        phrases, phrase_index = get_phrases(arr, dlg_len, c, manager_phrases_index) 
        bye = (chek_phrase(phrases, phrase_index, is_bye))  

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
    return arr

