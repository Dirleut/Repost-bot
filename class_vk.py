#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import time
import vk
import re
import calendar, datetime
import os.path


class VK_class:

    def __init__(self, token=None):
        self.session = vk.Session(access_token=token)
        self.api = vk.API(self.session)
        if token != None:
            self.is_offline = self.api.account.setOffline()
            print(self.is_offline)
        self.ourTime = 10800
        self.you = "You: "
        self.id_list = [] # ids and conv flags of the current dialogs

        print('VK class here')


    def get_post(self, offset=0, q=1, **kwargs):
        try:
            if kwargs['domain'] != "":
                post = self.api.wall.get(domain=kwargs['domain'], count=q, offset=offset)
            elif kwargs['owner_id']:
                post = self.api.wall.get(owner_id = kwargs['owner_id'], count=q, offset=offset)
            print(post)
            post = post[1]
            text = post['text']
            id = post['id']
            url = self.extract_attachment_url(post, src_size='src_xxbig')[0]
            type = self.extract_attachment_url(post, src_size='src_xxbig')[1]
            return text, url, type, id
        except:
            pass



    def friends_list(self, q):
        if not os.path.isfile("data.txt"):
            self.file = open("data.txt", "w", encoding="utf-8")
            self.file.close()
        friend_ids = self.api.friends.get(order='hints', count=q)
        friend_dict = dict()
        for i in range(0, len(friend_ids)):
            friend_dict[friend_ids[i]] = self.find_user(friend_ids[i])
            time.sleep(0.4)
        print(friend_dict)
        self.file = open("data.txt", "a", encoding="utf-8")
        self.file.write(str(friend_dict))
        self.file.close()


    def check(self):
        print("VK_class is alive.")


    def dt(self, u):
        return datetime.datetime.utcfromtimestamp(u + self.ourTime)


    def ut(self, d):
        return calendar.timegm(d.timetuple())


    def extract_title(self, string):
        title = string['title']
        result = ""
        if title != ' ... ':
            result = title
        return result

    def extract_date(self, string):
        date = string["date"]
        return int(date)

    def extract_message(self, string):
        return string["body"]

    def extract_user_id(self, string):
        user_id = string["uid"]
        return int(user_id)

    def extract_user_name(self, string):
        first_name, last_name = string['first_name'], string['last_name']
        return first_name, last_name

    def find_user(self, id):
        string = str(self.api.users.get(user_id=id))
        first_name, last_name = 'xxx', 'yyy'
        try:
            patternLast_name = r"'last_name': '[А-Яа-яA-Za-zё]+'"
            match = re.search(patternLast_name, string)
            match = match.group()
            match = list(match)
            del match[0: 14]
            del match[-1]
            last_name = ''.join(match)
            patternFirst_name = r"'first_name': '[A-Яа-яA-Za-zё]+'"
            match = re.search(patternFirst_name, string)
            match = match.group()
            match = list(match)
            del match[0: 15]
            del match[-1]
            first_name = ''.join(match)
        except(AttributeError):
            pass
        return first_name, last_name


    def is_message_read(self, string):
        is_mess = string["read_state"]
        if is_mess == 1:
            result = True
        elif is_mess == 0:
            result = False
        return result


    def is_message_out(self, string):
        is_mess = string["out"]
        if is_mess == 1:
            result = True
        elif is_mess == 0:
            result = False
        return result


    def decor(self, i=13):
        return ("||"+"="*i+"||")


    def print_messages(self, q):
        last_id = 0
        messList = self.api.messages.get(count=q, out=0)
        del messList[0]
        messList.reverse()
        for i in range(0, len(messList)):
            id = self.extract_user_id(messList[i])
            title = self.extract_title(messList[i])

            message = ""
            if self.is_message_out(messList[i]):
                message += self.you
            message += str(self.extract_message(messList[i]))
            message += " " + str(chr(897))
            if self.is_message_read(messList[i]):
                messagel = list(message)
                del messagel[-1]
                message = ''.join(messagel)

            dateU = self.extract_date(messList[i])
            date = self.dt(dateU)

            if title != "":
                print("  "+title)

            if last_id != id:
                (first_name, last_name) = self.find_user(id)
                name = first_name + " " + last_name
                #self.decor(len(name))
                print("  "+name)
                #self.decor(len(name))

            print(message)
            print(date)

            #last_title = title
            last_id = id
            time.sleep(0.2)
        #self.decor(1)


    def get_dialogs(self, q=15, offset=0):
        self.id_list = []
        result = ""
        diagList = self.api.messages.getDialogs(count=q, offset=offset, preview_length=100)
        del diagList[0]
        for i in range(0, len(diagList)):
            print(diagList[i])
            id = self.extract_user_id(diagList[i])

            ###Updates id list
            if 'chat_id' in diagList[i]:
                self.id_list.append([diagList[i]['chat_id'], 1])
            else:
                self.id_list.append([id, 0])
             ###chat id or user id

            title = self.extract_title(diagList[i])

            url = ""
            if 'attachment' in diagList[i]:
                url = self.extract_attachment_url(diagList[i])

            (first_name, last_name) = self.find_user(id)
            message = ""
            if self.is_message_out(diagList[i]):
                message += self.you
            message += str(self.extract_message(diagList[i]))
            message += " " + str(chr(897))
            if self.is_message_read(diagList[i]):
                messagel = list(message)
                del messagel[-1]
                message = ''.join(messagel)

            dateU = self.extract_date(diagList[i])
            date = self.dt(dateU)
            result += str(i+offset+1) + ")" + '\n' + self.decor()
            if title != "":
                result += '\n' + title

            result += '\n' + first_name + " " + last_name

            if message != "":
                result += '\n' + message

            if url != "":
                if message == "":
                    result += url + '\n'
                result +=  url
            result += '\n' + str(date) + '\n'
            time.sleep(0.3)
        print(self.id_list)
        return result


    def extract_attachment_url(self, dicti, src_size = 'src_big'):
        try:
            url = ""
            attachment = dicti['attachment']
            if attachment['type'] == 'photo':
                url = attachment['photo'][src_size]
            elif attachment['type'] == 'doc':
                url = attachment['doc']['url']
            elif attachment['type'] == 'video':
                url = attachment['video']['image_big']
            return url, attachment['type']
        except:
            pass


    def get_chat(self, id, conv, q=15, offset=0):
        result = ""
        first_name, last_name = '*','#'
        history = []
        #optimize this
        #sent messages are not shown
        if conv == 1:
            i = 0 - offset
            j = 0
            while i != q:
                time.sleep(0.2)
                mi = self.api.messages.get(count=100, offset=j)
                del mi[0]
                time.sleep(0.3)
                mo = self.api.messages.get(count=12, out=1, offset=j)
                del mo[0]
                mess = mi + mo
                print(mess)
                for m in range(0, len(mess)):
                    if 'chat_id' in mess[m]:
                        if mess[m]['chat_id'] == id:
                            if i >= 0:
                                history.append(mess[m])
                                #print(mess[j])
                            i += 1
                            if i == q:
                                break
                            #print(i)
                j += 100

        elif conv == 0:
            history = self.api.messages.getHistory(user_id=id, count=q, offset=offset)
            (first_name, last_name) = self.find_user(id)
            result += '\n' + first_name + ' ' + last_name
            del history[0]
        history.reverse()

        for i in range(0, len(history)):
            print(history[i])
            url = ""
            if 'attachment' in history[i]:
                url = self.extract_attachment_url(history[i])

            if conv == 1:
                (first_name, last_name) = self.find_user(history[i]['uid'])

            message = ""
            if self.is_message_out(history[i]):
                message += self.you
            message += str(self.extract_message(history[i]))
            message += " " + str(chr(897))
            if self.is_message_read(history[i]):
                messagel = list(message)
                del messagel[-1]
                message = ''.join(messagel)

            dateU = self.extract_date(history[i])
            date = self.dt(dateU)
            result += '\n' + self.decor()

            if conv == 1:
                result += '\n' + first_name + " " + last_name

            if message != "":
                result += '\n' + message

            if url != "":
                if message == "":
                    result += url + '\n'
                result += url
            result += '\n' + str(date)
            time.sleep(0.5)
        return result


    def get_account_info(self):
        result = ""
        info = self.api.account.getProfileInfo()

        name = self.extract_user_name(info)
        result += str(name[0]+" "+name[1])

        if info['status'] != '':
            result += "\nStatus: " + info['status']

        if info['bdate'] != '':
            result += "\n" + info['bdate']

        title = self.extract_title(info['country'])
        t = False
        if title != '':
            result += "\n" + title
            t = True
        if info['home_town'] != '':
            if not t:
                result += '\n'
            result += info['home_town']
        result += "\nhttps://vk.com/" + info['screen_name']
        return result


    def send_message(self, id, conv, message):
        self.is_offline = self.api.account.setOffline()
        if conv == 1:
            m = self.api.messages.send(chat_id = id, message=message)
        elif conv == 0:
            m = self.api.messages.send(user_id = id, message=message)
        self.is_offline = self.api.account.setOffline()

#a = VK_class("5cbee70150345e3861cc4086a9db4040b68c8fc5adafe5d6239dd7cea1a1f0171ba2f91d129b0fed09bda")
#post = a.get_post(7, 1 , domain="why_down_town")
#print(post)











