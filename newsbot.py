import telebot
import feedparser
import time
import html
import re
import os
from datetime import datetime

# ------------------- Bot Configuration -------------------
TOKEN = os.getenv("BOT_TOKEN") 
CHANNEL_ID = os.getenv("CHANNEL_ID")

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

# ------------------- Keywords & Hashtags -------------------
KEYWORDS = [
    "Gold", "Silver", "XAU", "XAG", 
    "Bitcoin", "BTC", "Crypto", "Ethereum",
    "Fed", "Federal Reserve", "Powell", "Interest Rate", 
    "Inflation", "CPI", "USD", "EUR", "Recession", "Market", "Oil"
]

posted_links = set()

def clean_html_tags(text):
    if not text: return ""
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text).strip() # strip عشان يشيل المسافات الزيادة

def get_smart_hashtags(text):
    tags = []
    text_lower = text.lower()
    
    if "gold" in text_lower or "xau" in text_lower:
        tags.extend(["#Gold", "#XAUUSD", "#Commodities"])
    if "silver" in text_lower or "xag" in text_lower:
        tags.extend(["#Silver", "#XAGUSD"])
    if "bitcoin" in text_lower or "btc" in text_lower or "crypto" in text_lower:
        tags.extend(["#Bitcoin", "#BTC", "#Crypto"])
    if "fed" in text_lower or "rate" in text_lower:
        tags.extend(["#Fed", "#Economy"])
    if "oil" in text_lower:
        tags.extend(["#Oil", "#Energy"])
        
    tags.append("#GlobalMarkets")
    return " ".join(list(set(tags)))

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

                # --- التعديل هنا: محاولة استخراج الملخص بذكاء ---
                raw_summary = ""
                if hasattr(entry, 'summary'):
                    raw_summary = entry.summary
                elif hasattr(entry, 'description'):
                    raw_summary = entry.description
                
                # تنضيف الملخص
                clean_summary = clean_html_tags(raw_summary)
                
                # لو الملخص طلع فاضي بعد التنضيف، حط جملة بديلة
                if not clean_summary or len(clean_summary) < 10:
                    clean_summary = "Check the link below for full details and charts."

                # تقصير الملخص لو طويل
                if len(clean_summary) > 300:
                    clean_summary = clean_summary[:300] + "..."
                
                clean_summary = html.escape(clean_summary)

                # دمج للبحث
                content_to_check = (title + " " + clean_summary)
                
                if any(keyword in content_to_check for keyword in KEYWORDS):
                    
                    hashtags = get_smart_hashtags(content_to_check)
                    
                    message = (
                        f"🚨 <b>{title}</b>\n\n"
                        f"📝 <i>{clean_summary}</i>\n\n"
                        f"{hashtags}\n\n"
                        f"🔗 <a href='{clean_link}'>Read Full Story</a>"
                    )

                    try:
                        bot.send_message(CHANNEL_ID, message, parse_mode='HTML', disable_web_page_preview=False)
                        print(f"✅ Posted: {entry.title}")
                        # سطر عشان نشوف في اللوج الملخص كان ايه
                        print(f"   Summary: {clean_summary[:50]}...") 
                        posted_links.add(raw_link)
                        time.sleep(2)
                    except Exception as send_error:
                        print(f"❌ Failed to send message: {send_error}")
                    
        except Exception as e:
            print(f"⚠️ Error with feed {feed_url}: {e}")

# ------------------- Main Loop -------------------
print("News Bot v2.1 initialized...")
while True:
    check_and_post_news()
    time.sleep(60)
