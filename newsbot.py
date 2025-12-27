import telebot
import feedparser
import time
import html
import os  # مكتبة عشان نقرأ المتغيرات من السيرفر
from datetime import datetime

# ------------------- إعدادات البوت (من السيرفر) -------------------
# هنا بنقوله لو ملقيتش التوكن في السيرفر، استخدم اللي مكتوب ده كـ احتياطي (للتجربة)
TOKEN = os.getenv("BOT_TOKEN") 
CHANNEL_ID = os.getenv("CHANNEL_ID")

# تأكد إن القيم موجودة
if not TOKEN or not CHANNEL_ID:
    print("Error: BOT_TOKEN or CHANNEL_ID not found in environment variables!")
    # ممكن تحط التوكن هنا مؤقتاً لو مش عايز تستخدم Environment Variables بس مش مستحسن
    # TOKEN = "7967418879:AAEfYYV1jEmyIJxOutZsxFITuhqrCWKZfRA"
    # CHANNEL_ID = "@Egy_GoldPrice"

bot = telebot.TeleBot(TOKEN)

# ------------------- Global News Sources (English) -------------------
RSS_FEEDS = [
    "https://www.investing.com/rss/news_25.rss",        # Commodities
    "https://www.investing.com/rss/news_1.rss",         # Forex
    "https://www.coindesk.com/arc/outboundfeeds/rss/",  # Crypto
    "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=10000664" # CNBC
]

# ------------------- Keywords -------------------
KEYWORDS = [
    "Gold", "Silver", "XAU", "XAG", 
    "Bitcoin", "BTC", "Crypto", "Ethereum",
    "Fed", "Federal Reserve", "Powell", "Interest Rate", 
    "Inflation", "CPI", "USD", "EUR", "Recession", "Market"
]

posted_links = set()

def check_and_post_news():
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Checking for global news...")
    
    for feed_url in RSS_FEEDS:
        try:
            feed = feedparser.parse(feed_url)
            
            for entry in feed.entries[:5]:
                title = html.escape(entry.title)
                raw_link = entry.link
                clean_link = html.escape(raw_link)
                
                if raw_link in posted_links:
                    continue

                summary = html.escape(entry.summary) if 'summary' in entry else ""
                content_to_check = (title + " " + summary)
                
                if any(keyword in content_to_check for keyword in KEYWORDS):
                    message = (
                        f"🚨 <b>BREAKING NEWS</b>\n\n"
                        f"📌 {title}\n\n"
                        f"🔗 <a href='{clean_link}'>Read Full Story</a>\n"
                        f"___\n"
                        f"🤖 <i>Live updates on {CHANNEL_ID}</i>"
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
print("Global News Bot initialized...")
while True:
    check_and_post_news()
    time.sleep(60)