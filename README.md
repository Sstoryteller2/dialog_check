# dialog_check
script for search NER in dialogs (russion). Spacy
Скрипт для парсинга диалогов

## Запуск:
Клонируете репозиторий, запускаете

```pip install -r requirements.txt```

(установятся numpy, pandas, spacy и библиотека ru_core_news_lg ~500mb)  

В папку с файлами копируете файл test_data.csv (файл должен быть с таким названием, или нужно поменять в main.py), запускаете 

```./main.py  ```

Результат выполнения скрипта сохраняется в **файл res_data.csv**

## Как всё работает:
Под каждую задачу написана функция, которая ищет нужные сущности.  
Общий подход такой: 
1. Выделяем id диалогов, на основе них фильтруем данные
2. Выбираем фразы manager
3. Работаем с тремя (можно варьировать) первыми фаразами для выделения приветствия и представления и тремя последними для прощания.
4. Всё полученное формируем в таблицу и сохраняем.

Состав проекта:
1. function.py - все функции, которые используются
2. synonyps.py - списки синонимов
3. main.py - исполнительный файл скрипта

Собственно задание:
### а) реплики с приветствием
Функция is_greet_in_phrase.  

Проверяет леммы токенов во фразе на соответвие в списке синонимов ('здравствовать', 'добрый', 'привет', 'приветствовать'), должно охватывать большинство возможных приветствий.

### b-c) реплики, где менеджер представил себя
функция is_introduce_in_phrase  

Проверяем на наличие именнованной сущиности Person, смотрим отношение nsubj к главному слову из списка для фраз "меня зовут", "моё имя", "с вами говорит", на всякий случай проверяем по леммам.  

Проверяем через зависимости, чтобы исключить другие упомининания имён (в датасете в первых фразах есть обращения к клиентам по имени).  

Отдельно сделал учёт конструкции типа "Это Ольга", когда нет приветствия и слов из синонимческого ряда. 

### d) Извлекать название компании
Самая сложная часть, функция  get_company_name.  

При помощи spacy, ntlk и natasha я не смог поймать в NER названия компаний. Как вариант можно попробовать натренировать spacy на реестре организаций, но быстро найти готовый сет не получилось. Поэтому я пошёл другим путём.

Чем ловить при помощи нейросети NER, можно исходить из того, что название компании известно (клиент). Формируем из них список всех компаний, и проверяем по списку. Учитывая технологии speech-to-text, добавил функцию, которая выбирает компании по максимальной схожести (если будет разнобой в написаниях). Сам момент называния компании ловится по слову компания.

### e) Извлекать реплики с прощанием
функция is_bye

Просто проверяем на список прощальных фраз. Эту часть можно усилить либо синтаксическими контрукциями, либо натренировать на более большом объёме данных.  
Синтакисческая контрукция исользуется для фраз включающися в себя слово "до" (До завтра, до встречи). 

### f) Проверка требований и итоговая таблица
При формиаровании столбца "insight", нужно учитывать случаи, когда, например нет представления или менедждер не поздаровался, когда несколько условий выполнено в одной фразе. Тоже самое и с прощанием.

Я записал все условия связанные с представлением, в первую фразу диалога, и дальше во все фразы, где условия выполняются. Проверка прощания, записана в последнюю фразу менеджера.

- greeting=True/False - приветствие
- introduction=True/False - представление
- company=True/False - названа компания
- bying=True/False - прощание

На всякий случай сделал в таблице дополнительные колонки по названию пунктов задания, чтобы не было путаницы)
- a. Извлекать реплики с приветствием – где менеджер поздоровался. 
- b. Извлекать реплики, где менеджер представил себя. 
- c. Извлекать имя менеджера. 
- d. Извлекать название компании. 
- e. Извлекать реплики, где менеджер попрощался.
- f. Проверять требование к менеджеру: «В каждом диалоге обязательно необходимо поздороваться и попрощаться с клиентом»










