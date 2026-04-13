import os
import sys
import time
import threading # ضروري للفصل

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

# جلب الإعدادات
GEMINI_KEY = os.environ.get('GEMINI_KEY')
TELE_TOKEN = os.environ.get('TELE_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')

genai.configure(api_key=GEMINI_KEY)
ai_model = genai.GenerativeModel('gemini-1.5-flash')
bot = telebot.TeleBot(TELE_TOKEN)

# دالة التحليل التي ستعمل في الخلفية
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
                
                if any(word in res_text for word in ["دخول", "هدف", "نقطة"]):
                    bot.send_message(CHAT_ID, f"🎯 إشارة ذهب:\n\n{res_text}")
                    log("📩 تم إرسال إشارة لتليجرام")
            
            # انتظر 5 دقائق قبل الفحص التالي (عشان ما نستهلك كوتا Gemini)
            time.sleep(300) 
        except Exception as e:
            log(f"❌ خطأ في حلقة المراقبة: {e}")
            time.sleep(60) # انتظر دقيقة وحاول مرة ثانية في حال الخطأ

@app.route('/')
def home():
    log("⏰ الكرون جوب وصل.. السيرفر مستيقظ")
    return "Bot is LIVE and Monitoring...", 200

if __name__ == "__main__":
    log("🚀 تشغيل السيرفر الاحترافي...")
    
    # تشغيل مراقب الذهب في "خيط" منفصل عن السيرفر
    monitor_thread = threading.Thread(target=background_monitor)
    monitor_thread.daemon = True # يغلق بمجرد إغلاق البرنامج
    monitor_thread.start()
    
    try:
        bot.send_message(CHAT_ID, "🚀 القناص استيقظ وبدأ المراقبة المستمرة!")
        # السيرفر هون بس وظيفته يرد على الكرون جوب عشان ريندر ما يطفي
        serve(app, host='0.0.0.0', port=10000)
    except Exception as e:
        log(f"💥 فشل تشغيل السيرفر: {e}")
        
