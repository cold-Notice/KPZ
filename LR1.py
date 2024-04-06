import pandas as pd  # Импорт библиотеки pandas для работы с таблицами
from datetime import datetime  # Импорт класса datetime для работы с датами и временем
import os  # Импорт модуля os для работы с файловой системой

filename = 'filename.csv'  # Название файла для сохранения данных

# Проверка наличия файла и чтение его, если он существует
if os.path.isfile(filename):
    df = pd.read_csv(filename)  # Чтение файла, если он существует
else:
    # Создание нового DataFrame, если файл не найден
    df = pd.DataFrame(columns=['year', 'month', 'day', 'hour', 'minute', 'second'])

now = datetime.now()  # Получение текущей даты и времени

new_row = now.strftime('%Y %m %d %H %M %S').split()  
df.loc[len(df)] = new_row  # Добавление новой строки в DataFrame

df.to_csv(filename, index=False)  # Сохранение обновлённого DataFrame в файл без индекса

print(df)  # Вывод содержимого DataFrame на экран
