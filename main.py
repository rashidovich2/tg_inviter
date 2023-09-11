from datetime import date, datetime
import json
import os
import time
from telethon import TelegramClient

from inviter import Inviter
from lists import Lists
from config import CH_FROM, CH_TO

lists = Lists()
PHONES_LIST = lists.get_phones_list()

#Получение списков из файла phones.json
BANNED_PHONES_LIST = lists.get_banned_phones_list()
CHECK_PHONES_LIST = lists.get_check_list()

#Создание файлов сессии по номеру если их нет
for number in PHONES_LIST:
    #Если номер не забанен
    if number not in BANNED_PHONES_LIST:
        #Если файл сессии существует
        if os.path.exists(f"{number}.session"):
            #Ничего не делать
            continue
        #Вывод номера в консоль
        print(number)
        #Запрос на получение кода и вход
        TelegramClient(number, 6087612,
                       "1148dcdf0ec9b2e68e97b0fa104f14a4").start(number).disconnect()

def main():
    i = 0

    #Главный цикл
    while True:
        try:
            #Получить списки из phones.json
            BANNED_PHONES_LIST = lists.get_banned_phones_list()
            CHECK_PHONES_LIST = lists.get_check_list()
            if i < len(PHONES_LIST):
                
                number = PHONES_LIST[i]
                i += 1

                #Если номер в режиме ожидания
                if number in CHECK_PHONES_LIST:
                    #Получение текущей даты и времени
                    cur_day = date.today().day #Текущий день
                    cur_hour = datetime.now().hour #Текущий час
                    cur_min = datetime.now().minute #Текущая минута
                    cur_sec = datetime.now().second #Текущая секунда
                    
                    #Проверить если номеру пора уходить из режима ожидания
                    if (cur_day >= CHECK_PHONES_LIST[number][0] and
                        cur_hour >= CHECK_PHONES_LIST[number][1] and
                        cur_min >= CHECK_PHONES_LIST[number][2] and
                        cur_sec >= CHECK_PHONES_LIST[number][3]):

                            #Получение текущих данных из файла phones.json
                            data = lists.get_full_phones_list()

                            #Удалить из списка номеров в режиме ожидания
                            del data['check'][number]
                            #Обнуление количества запросов по номеру
                            data['request_count'][number] = 0

                            #Запись данных в файл phones.json
                            with open('./lists/phones.json', 'w') as f:
                                dump = json.dump(data, f, indent=4)

                #Если номер не забанен и не в режиме ожидания
                if (number not in BANNED_PHONES_LIST and
                    number not in CHECK_PHONES_LIST):

                        #Инициализация инвайтера
                        inviter = Inviter(number)

                        async def bot_main():
                            #Парсинг пользователей в файл users.list
                            await inviter.parse_users(CH_FROM)
                            #Инвайтинг в группу
                            await inviter.invite_from(CH_TO)
                            #Остановка инвайтера
                            await inviter.end()

                        #Если бот успешно залогинился
                        if inviter.login() == True:
                            #Запустить bot_main
                            inviter.client.loop.run_until_complete(bot_main())
            else:
                i = 0
                time.sleep(2)

        #Если CTRL+C нажато
        except KeyboardInterrupt:
            print("Бот Остановлен!")
            break


if __name__ == '__main__':
    main()
