import random
import sys
import time
from datetime import date, datetime
from tqdm import tqdm
import socks

from telethon.sync import TelegramClient
from telethon.tl.functions.channels import InviteToChannelRequest
from telethon.errors.rpcerrorlist import (UserPrivacyRestrictedError, 
                                          UserNotMutualContactError,
                                          FloodWaitError, 
                                          PeerFloodError, 
                                          UserChannelsTooMuchError, 
                                          UserDeactivatedBanError, 
                                          PhoneNumberBannedError,
                                          UsernameInvalidError,
                                          ChatWriteForbiddenError)

from lists import Lists
import config

class Inviter:
    def __init__(self, phone):
        self.phone = phone
        self.lists = Lists()
        self.client = None
        self.me = None

    def get_time_str(self):
        return datetime.now().strftime("%H:%M:%S")

    def login(self):
        try:
            if config.PROXY_ENABLED:
                s = socks.socksocket()
                rnd_proxy = random.choice(config.PROXY_IPS).split(":")
                print(f"Подключение к телеграмм с прокси {rnd_proxy}!")
                self.client = TelegramClient(self.phone, 6087612, "1148dcdf0ec9b2e68e97b0fa104f14a4", proxy=s.set_proxy(socks.HTTP, rnd_proxy[0], rnd_proxy[1]) )
                self.client.start(self.phone)
            else:
                print(f"Подключение к телеграмм без прокси!")
                self.client = TelegramClient(self.phone, 6087612, "1148dcdf0ec9b2e68e97b0fa104f14a4")
                self.client.start(self.phone)

            return True
        except PhoneNumberBannedError:
            print(f"{self.get_time_str()} | Ошибка: аккаунт {self.phone} был удалён!")
            self.lists.add_banned_phone(self.phone)
            return False

    async def invite(self, users, channel):
        await self.client(InviteToChannelRequest(channel=await self.client.get_entity(channel), users=users))

    async def parse_users(self, channel):
        try:
            ch_users = await self.client.get_participants(channel)
        except TypeError:
            print("Ошибка: выберите другой чат для парсинга пользователей!")
            return False
        except FloodWaitError as e:
            cur_time = self.get_time_str()
            print(
                f"{cur_time} | Ошибка: Таймаут на {e.seconds} секунд, это примерно {round(e.seconds / 60)} минут \n"
            )
            if config.CHECK_TIMEOUT:
                for i in tqdm(range(e.seconds)):
                    time.sleep(1)
            else:
                cur_day = date.today().day
                cur_hour = datetime.now().hour
                cur_min = datetime.now().minute
                cur_sec = datetime.now().second
                print(f"{cur_time} | Аккаунт {self.phone} уходит в режим ожидания до {cur_day + 1} числа и {cur_hour + 1} часов!")
                self.lists.add_check(self.phone, [cur_day + 1, cur_hour + 1, cur_min, cur_sec])
                return False
        except:
            print(f"Неизвестная ошибка: {sys.exc_info()}")

        invited_l = self.lists.get_invited_list()
        banned_l = self.lists.get_ban_list()
        users_l = self.lists.get_users_list()

        print(f"Найдено {len(ch_users)} пользователей!")

        for user in ch_users:
            username = user.username

            if (not user.bot and
                username != None and
                username not in banned_l and
                username not in users_l and
                    username not in invited_l):
                self.lists.add_user(username)

    async def invite_from(self, to):
        self.me = await self.client.get_me()
        print(f"{self.get_time_str()} | Бот {self.me.first_name} начал инвайт!")

        
        users = self.lists.get_users_list()
        
        random.shuffle(users)

        ctr = 0

        try:
            invited = self.lists.get_request_count_list()[self.phone]
        except KeyError:
            invited = 0
            
        not_invited = 0

        for j, user in enumerate(users):
            ctr = j+1
            cur_time = self.get_time_str()
            if invited == config.INV_CNT:
                cur_day = date.today().day
                cur_hour = datetime.now().hour
                cur_min = datetime.now().minute
                cur_sec = datetime.now().second
                print(f"{cur_time} | Аккаунт {self.me.first_name} набрал {config.INV_CNT} инвайтов !")
                print(f"{cur_time} | Аккаунт {self.me.first_name} уходит в режим ожидания до {cur_day + 1} числа и {cur_hour + 1} часов!")
                self.lists.add_check(self.phone, [cur_day + 1, cur_hour + 1, cur_min, cur_sec])
                break

            if user != '':
                try:
                    await self.invite([user], to)
                    print(f"{cur_time} | {user} приглашён!")
                    invited += 1
                    self.lists.add_invite(user)
                except UserPrivacyRestrictedError:
                    print(f"{cur_time} | Ошибка: {user} не приглашён!")
                    print(f"Пользователь {user} запретил приглашать себя!")
                    not_invited += 1
                    time.sleep(config.ERR_KD)
                    self.lists.add_ban(user)
                    continue
                except UserChannelsTooMuchError:
                    print(f"{cur_time} | Ошибка: {user} не приглашён!")
                    print(f"Пользователь {user} ебанутый!")
                    not_invited += 1
                    time.sleep(config.ERR_KD)
                    self.lists.add_ban(user)
                    continue
                except UserDeactivatedBanError:
                    print(f"{cur_time} | Ошибка: {user} не приглашён!")
                    print(f"Пользователь {user} удалён!")
                    not_invited += 1
                    time.sleep(config.ERR_KD)
                    self.lists.add_ban(user)
                    continue
                except UserNotMutualContactError:
                    print(f"{cur_time} | Ошибка: {user} не приглашён!")
                    print(f"Пользователь {user} не взамный контакт !")
                    not_invited += 1
                    time.sleep(config.ERR_KD)
                    self.lists.add_ban(user)
                    continue
                except (ValueError, UsernameInvalidError):
                    print(f"{cur_time} | Ошибка: {user} не приглашён!")
                    print(f"Пользователя с ником {user} не существует!")
                    not_invited += 1
                    time.sleep(config.ERR_KD)
                    self.lists.add_ban(user)
                    continue
                except FloodWaitError as e:
                    print(
                        f"{cur_time} | Ошибка: Таймаут на {e.seconds} секунд, это примерно {round(e.seconds / 60)} минут \n",
                        f"За время работы бот успел пригласить {invited} пользователей"
                    )
                    if config.CHECK_TIMEOUT:
                        for i in tqdm(range(e.seconds)):
                            time.sleep(1)
                    else:
                        cur_day = date.today().day
                        cur_hour = datetime.now().hour
                        cur_min = datetime.now().minute
                        cur_sec = datetime.now().second

                        sec = e.seconds + cur_sec
                        sec = sec % (24 * 3600)
                        hour = sec // 3600
                        sec %= 3600
                        min = sec // 60
                        sec %= 60

                        print(f"{cur_time} | Аккаунт {self.me.first_name} уходит в режим ожидания на {hour} часов, {min} минут, {sec} секунд")
                        self.lists.add_check(self.phone, [cur_day, cur_hour+hour, cur_min+min, sec])
                        break
                except ChatWriteForbiddenError:
                    print(
                        f"{cur_time} | Ошибка: чат {to} недоступен, возможно вы не вошли в него!"
                    )
                    break
                except PeerFloodError as e:
                    print(f"{cur_time} | Ошибка: Слишком много запросов!")
                    cur_day = date.today().day
                    cur_hour = datetime.now().hour
                    cur_min = datetime.now().minute
                    cur_sec = datetime.now().second
                    print(f"{cur_time} | Аккаунт {self.me.first_name} уходит в режим ожидания до {cur_day + 1} числа и {cur_hour+1} часов!")
                    self.lists.add_check(self.phone, [cur_day + 1, cur_hour+1, cur_min, cur_sec])
                    break
                except:
                    print(f"{cur_time} | Неизвестная ошибка: ", sys.exc_info())
                
                try:
                    time.sleep(config.INV_KD)
                except KeyboardInterrupt:
                    break

        self.lists.set_request_count(self.phone, invited)
        print(f"{cur_time} | Бот {self.me.first_name} закончил инвайт на {ctr} юзере!")
        print(f"Приглашено {invited} юзеров")
        print(f"Не приглашено {not_invited} юзеров")
        print("__________________\n")

    async def end(self):
        await self.client.disconnect()
