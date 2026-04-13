import os
import sys
import time
import threading

def log(msg):
    print(msg, flush=True)

# استيراد المكتبات مع تجاوز التنبيهات
try:
    from flask import Flask
    from waitress import serve
    import yfinance as yf
    import telebot
    import google.generativeai as genai
    log("✅ المكتبات جاهزة")
except Exception as e:
    log(f"❌ خطأ مكتبات: {e}")

app = Flask('')

# دالة التحليل
def background_monitor():
    log("📡 بدأت المراقبة...")
    # جلب المفاتيح داخل الدالة لضمان قرائتها بعد تشغيل السيرفر
    G_KEY = os.environ.get('GEMINI_KEY')
    T_TOKEN = os.environ.get('TELE_TOKEN')
    C_ID = os.environ.get('CHAT_ID')
    
    if not G_KEY or not T_TOKEN:
        log("⚠️ تحذير: المفاتيح مش مقروءة حالياً، رح أحاول كمان شوي...")
    
    while True:
        try:
            # إعادة جلب المفاتيح في كل دورة لو كانت ناقصة
            if not G_KEY: G_KEY = os.environ.get('GEMINI_KEY')
            
            genai.configure(api_key=G_KEY)
            ai_model = genai.GenerativeModel('gemini-1.5-flash')
            bot = telebot.TeleBot(T_TOKEN)
            
            gold = yf.Ticker("GC=F")
            df = gold.history(period="1d", interval="15m")
            if not df.empty:
                current_price = df['Close'].iloc[-1]
                log(f"📊 السعر الحالي: {current_price:.2f}")
                
                prompt = f"Analysis Gold SMC for price {current_price:.2f}. Give entry or wait."
                response = ai_model.generate_content(prompt)
                
                if any(word in response.text for word in ["دخول", "target", "entry", "🎯"]):
                    bot.send_message(C_ID, f"🎯 إشارة ذهب:\n{response.text}")
                    log("📩 تم الإرسال")
            
            time.sleep(300) 
        except Exception as e:
            log(f"❌ خطأ بسيط: {e}")
            time.sleep(30)

@app.route('/')
def home():
    return "Bot is alive", 200

if __name__ == "__main__":
    # تشغيل خيط المراقبة
    monitor_thread = threading.Thread(target=background_monitor)
    monitor_thread.daemon = True
    monitor_thread.start()
    
    port = int(os.environ.get("PORT", 10000))
    log(f"🚀 السيرفر شغال على بورت {port}")
    try:
        serve(app, host='0.0.0.0', port=port)
    except Exception as e:
        log(f"💥 فشل السيرفر: {e}")
