import json


class Lists:

    # USERS GETTERS

    def get_invited_list(self):
        with open('./lists/invited.list', 'r') as f:
            return f.read().split('\n')

    def get_ban_list(self):
        with open('./lists/ban.list', 'r') as f:
            return f.read().split('\n')

    def get_users_list(self):
        with open('./lists/users.list', 'r') as f:
            return f.read().split('\n')

    # USERS ADDERS

    def add_ban(self, ban):
        with open('./lists/ban.list', 'a') as f:
            f.write(f"{ban}\n")

    def add_user(self, user):
        with open('./lists/users.list', 'a') as f:
            f.write(f"{user}\n")

    def add_invite(self, invite):
        with open('./lists/invited.list', 'a') as f:
            f.write(f"{invite}\n")

    # PHONES GETTERS

    def get_full_phones_list(self):
        with open('./lists/phones.json', 'r') as f:
            return json.load(f)

    def get_check_list(self):
        return self.get_full_phones_list()['check']

    def get_phones_list(self):
        return self.get_full_phones_list()['avaliable']

    def get_banned_phones_list(self):
        return self.get_full_phones_list()['banned']
    
    def get_request_count_list(self):
        return self.get_full_phones_list()['request_count']

    # PHONES ADDERS

    def add_check(self, num, time):
        data = self.get_full_phones_list()

        data['check'][num] = time

        with open('./lists/phones.json', 'w') as f:
            dump = json.dump(data, f, indent=4)

    def add_banned_phone(self, num):
        data = self.get_full_phones_list()

        data['banned'].append(num)

        with open('./lists/phones.json', 'w') as f:
            dump = json.dump(data, f, indent=4)
    
    def add_avaliable_phone(self, num):
        data = self.get_full_phones_list()

        data['avaliable'].append(num)

        with open('./lists/phones.json', 'w') as f:
            dump = json.dump(data, f, indent=4)
    
    def set_request_count(self, num, count):
        data = self.get_full_phones_list()

        data['request_count'][num] = count

        with open('./lists/phones.json', 'w') as f:
            dump = json.dump(data, f, indent=4)
