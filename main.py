import os
import sys
import time
import threading

def log(msg):
    print(msg, flush=True)

try:
    from flask import Flask
    from waitress import serve
    import yfinance as yf
    import telebot
    import google.generativeai as genai
    log("✅ تم استيراد جميع المكتبات بنجاح")
except Exception as e:
    log(f"❌ خطأ في المكتبات: {e}")
    sys.exit(1)

app = Flask('')

# جلب الإعدادات - تأكد من وجودها في Render Dashboard -> Environment
GEMINI_KEY = os.environ.get('GEMINI_KEY') or os.environ.get('GOOGLE_API_KEY')
TELE_TOKEN = os.environ.get('TELE_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')

# فحص وجود المفاتيح قبل البدء
if not GEMINI_KEY or not TELE_TOKEN:
    log("❌ خطأ: لم يتم العثور على المفاتيح (GEMINI_KEY أو TELE_TOKEN) في الإعدادات!")
    sys.exit(1)

# إعداد Gemini
try:
    genai.configure(api_key=GEMINI_KEY)
    ai_model = genai.GenerativeModel('gemini-1.5-flash')
    bot = telebot.TeleBot(TELE_TOKEN)
except Exception as e:
    log(f"❌ فشل إعداد API الـ AI: {e}")

def background_monitor():
    log("📡 بدأت عملية المراقبة في الخلفية...")
    while True:
        try:
            gold = yf.Ticker("GC=F")
            df = gold.history(period="1d", interval="15m")
            if not df.empty:
                current_price = df['Close'].iloc[-1]
                log(f"📊 فحص دوري.. السعر الحالي: {current_price:.2f}")
                
                prompt = f"حلل الذهب SMC للسعر {current_price:.2f}. أعطِ توصية دخول قوية فقط أو قل انتظار."
                response = ai_model.generate_content(prompt)
                res_text = response.text
                
                if any(word in res_text for word in ["دخول", "هدف", "نقطة", "Target", "Entry"]):
                    bot.send_message(CHAT_ID, f"🎯 إشارة ذهب جديدة:\n\n{res_text}")
                    log("📩 تم إرسال إشارة لتليجرام")
            
            time.sleep(300) # فحص كل 5 دقائق
        except Exception as e:
            log(f"❌ خطأ في حلقة المراقبة: {e}")
            time.sleep(60)

@app.route('/')
def home():
    log("⏰ الكرون جوب (أو مستخدم) زار الرابط.. السيرفر صاحي")
    return "Bot is LIVE and Monitoring Gold...", 200

if __name__ == "__main__":
    # إرسال رسالة تشغيل فورية للتأكد من التلجرام
    try:
        bot.send_message(CHAT_ID, "🚀 القناص استيقظ الآن! المراقبة مستمرة 24/5.")
        log("✅ أرسلت رسالة ترحيب لتليجرام")
    except Exception as e:
        log(f"❌ فشل إرسال رسالة التلجرام: {e}")

    monitor_thread = threading.Thread(target=background_monitor)
    monitor_thread.daemon = True
    monitor_thread.start()
    
    # البورت 10000 هو الافتراضي لـ Render
    port = int(os.environ.get("PORT", 10000))
    log(f"🚀 تشغيل السيرفر على Port {port}...")
    serve(app, host='0.0.0.0', port=port)
    
