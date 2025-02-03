import feedparser
import requests
import time
import re
import os

# === НАСТРОЙКИ ===
TELEGRAM_BOT_TOKEN = "ВАШ_ТОКЕН_ОТ_BOTFATHER"
CHAT_ID = "@ВАШ_КАНАЛ"
RSS_FEED_URL = "https://24tv.ua/rss/all.xml"
CHECK_INTERVAL = 900  # Проверка новых новостей каждые 15 минут (900 секунд)
SIGNATURE = "\n\n🔹 @UaNewsMain_24"  # Добавляем название канала в конце публикации
SENT_NEWS_FILE = "sent_news.txt"  # Файл для хранения опубликованных ссылок

# === Загружаем уже опубликованные новости ===
def load_sent_news():
    if os.path.exists(SENT_NEWS_FILE):
        with open(SENT_NEWS_FILE, "r") as file:
            return set(file.read().splitlines())
    return set()

# === Сохраняем отправленные новости в файл ===
def save_sent_news():
    with open(SENT_NEWS_FILE, "w") as file:
        file.write("\n".join(sent_news))

# === Инициализация списка отправленных новостей ===
sent_news = load_sent_news()

def extract_image_url(description):
    """Извлекаем URL изображения из HTML-кода в RSS."""
    match = re.search(r"<img.*?src=['\"](.*?)['\"].*?>", description)
    return match.group(1) if match else None

def send_telegram_message(title, description, link, image_url=None):
    """Отправляем сообщение в Telegram."""
    text = f"<b>📢 {title}</b>\n\n📰 {description}{SIGNATURE}\n\n🔗 <a href='{link}'>Читать полностью</a>"

    if image_url:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
        data = {"chat_id": CHAT_ID, "photo": image_url, "caption": text, "parse_mode": "HTML"}
    else:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        data = {"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"}

    requests.post(url, data=data)

def check_rss():
    """Проверяем RSS-ленту и отправляем новые новости в Telegram."""
    global sent_news
    feed = feedparser.parse(RSS_FEED_URL)
    
    for entry in feed.entries:
        if entry.link not in sent_news:  # Проверяем, публиковали ли мы эту новость
            description = re.sub(r"<.*?>", "", entry.summary.split("<a")[0])  # Убираем HTML
            image_url = extract_image_url(entry.summary)  # Получаем URL изображения
            send_telegram_message(entry.title, description, entry.link, image_url)
            sent_news.add(entry.link)  # Добавляем в список отправленных
            save_sent_news()  # Сохраняем изменения

# === Запуск бота ===
while True:
    check_rss()
    time.sleep(CHECK_INTERVAL)  # Ждём 15 минут перед следующей проверкой
