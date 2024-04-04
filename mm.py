import sys
from javascript import require, On, Once, console,off
from dotenv import load_dotenv, find_dotenv
import os
import socket
import time


mineflayer = require("mineflayer", "latest")
load_dotenv(find_dotenv())
domain = os.getenv("HOST")
host = socket.gethostbyname(domain)
port = os.getenv("PORT")
username = os.getenv("PLAYER")
auth = os.getenv("AUTH")
# 开始登陆
try:
    if auth == 'True':
        bot = mineflayer.createBot({
            "host": host,
            "port": port,
            "username": username,
            'auth': 'microsoft'
        })
    else:
        bot = mineflayer.createBot({
            "host": host,
            "port": port,
            "username": username
        })
except Exception as e:
    print(f'[server]连接错误：\n{e},将在5秒后退出程序')
    time.sleep(5)
    sys.exit(0)


@On(bot, "login")
def login(this):
    print(f'[server]成功登录')

@On(bot, "messagestr")
def message(this, message, *args):
    print(f'[server]{message}')


@On(bot, "kicked")
def kicked(this, reason, *a):
    print(f"I got kicked for {reason},{a}")


while True:
    line = sys.stdin.readline().strip()
    if sys.stdin.closed:
        break
    if line=='':
        continue
    elif line=='$$exit':
        print('正在离开服务器...')
        bot.quit()
        break
    bot.chat(line)

maps = {'login':login,
        'kicked':kicked,
        'messagestr':message}
for name,fun in maps.items():
    off(bot,name,fun)
# 关闭监听器

sys.exit()

