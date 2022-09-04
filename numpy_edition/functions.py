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