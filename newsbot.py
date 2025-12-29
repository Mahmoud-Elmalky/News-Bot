import telebot
import feedparser
import time
import html
import re  # مكتبة عشان تنضيف النصوص
import os
from datetime import datetime

# ------------------- Bot Configuration -------------------
TOKEN = os.getenv("BOT_TOKEN") 
CHANNEL_ID = os.getenv("CHANNEL_ID")

# Fallback for testing locally if env vars are missing
if not TOKEN:
    print("⚠️ Warning: Bot Token not found in environment variables.")

bot = telebot.TeleBot(TOKEN)

# ------------------- Global News Sources -------------------
RSS_FEEDS = [
    "https://www.investing.com/rss/news_25.rss",        # Commodities
    "https://www.investing.com/rss/news_1.rss",         # Forex
    "https://www.coindesk.com/arc/outboundfeeds/rss/",  # Crypto
    "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=10000664" # CNBC
]

# ------------------- Keywords & Hashtags Logic -------------------
KEYWORDS = [
    "Gold", "Silver", "XAU", "XAG", 
    "Bitcoin", "BTC", "Crypto", "Ethereum",
    "Fed", "Federal Reserve", "Powell", "Interest Rate", 
    "Inflation", "CPI", "USD", "EUR", "Recession", "Market", "Oil"
]

posted_links = set()

# دالة لتنضيف النص من أكواد HTML
def clean_html_tags(text):
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)

# دالة ذكية بتختار الهاشتاجات بناء على محتوى الخبر
def get_smart_hashtags(text):
    tags = []
    text_lower = text.lower()
    
    if "gold" in text_lower or "xau" in text_lower:
        tags.extend(["#Gold", "#XAUUSD", "#Commodities"])
    if "silver" in text_lower or "xag" in text_lower:
        tags.extend(["#Silver", "#XAGUSD"])
    if "bitcoin" in text_lower or "btc" in text_lower or "crypto" in text_lower:
        tags.extend(["#Bitcoin", "#BTC", "#Crypto", "#Blockchain"])
    if "fed" in text_lower or "rate" in text_lower or "powell" in text_lower:
        tags.extend(["#Fed", "#Economy", "#USEconomy"])
    if "oil" in text_lower:
        tags.extend(["#Oil", "#Energy"])
        
    # هاشتاجات ثابتة للقناة
    tags.append("#GlobalMarkets")
    
    # تحويل القائمة لنص واحد وإزالة التكرار
    return " ".join(list(set(tags)))

def check_and_post_news():
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Checking for global news...")
    
    for feed_url in RSS_FEEDS:
        try:
            feed = feedparser.parse(feed_url)
            
            for entry in feed.entries[:5]:
                # 1. تجهيز البيانات الأساسية
                title = html.escape(entry.title)
                raw_link = entry.link
                clean_link = html.escape(raw_link)
                
                if raw_link in posted_links:
                    continue

                # 2. استخراج وتنضيف الملخص
                raw_summary = entry.summary if 'summary' in entry else ""
                # بنشيل أي صور أو لينكات جوا الملخص عشان متبوظش شكل الرسالة
                clean_summary = clean_html_tags(raw_summary) 
                # تقصير الملخص لو طويل أوي (أول 250 حرف كفاية)
                if len(clean_summary) > 250:
                    clean_summary = clean_summary[:250] + "..."
                
                clean_summary = html.escape(clean_summary) # أمان إضافي

                # 3. دمج العنوان والملخص للبحث
                content_to_check = (title + " " + clean_summary)
                
                # 4. البحث عن الكلمات المفتاحية
                if any(keyword in content_to_check for keyword in KEYWORDS):
                    
                    # 5. توليد الهاشتاجات
                    hashtags = get_smart_hashtags(content_to_check)
                    
                    # 6. شكل الرسالة الجديد (احترافي)
                    message = (
                        f"🚨 <b>{title}</b>\n\n"
                        f"📝 <i>{clean_summary}</i>\n\n"
                        f"{hashtags}\n\n"
                        f"🔗 <a href='{clean_link}'>Read Full Story</a>"
                    )

                    try:
                        bot.send_message(CHANNEL_ID, message, parse_mode='HTML', disable_web_page_preview=False)
                        print(f"✅ Posted: {entry.title}")
                        posted_links.add(raw_link)
                        time.sleep(2)
                    except Exception as send_error:
                        print(f"❌ Failed to send message: {send_error}")
                    
        except Exception as e:
            print(f"⚠️ Error with feed {feed_url}: {e}")

# ------------------- Main Loop -------------------
print("News Bot v2.0 initialized...")
while True:
    check_and_post_news()
    time.sleep(60)
