import os
import sys
import time
import threading

def log(msg):
    print(msg, flush=True)

# استيراد المكتبات
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

def background_monitor():
    log("📡 بدأت المراقبة...")
    
    while True:
        try:
            # استخدام الاسم القياسي للمفتاح
            api_key = os.environ.get('GOOGLE_API_KEY')
            tele_token = os.environ.get('TELE_TOKEN')
            chat_id = os.environ.get('CHAT_ID')
            
            if not api_key or not tele_token:
                log("⚠️ تحذير: المفاتيح (GOOGLE_API_KEY أو TELE_TOKEN) مش موجودة في Environment Variables")
                time.sleep(30)
                continue

            # إعداد Gemini
            genai.configure(api_key=api_key)
            ai_model = genai.GenerativeModel('gemini-1.5-flash')
            bot = telebot.TeleBot(tele_token)
            
            # جلب بيانات الذهب
            gold = yf.Ticker("GC=F")
            df = gold.history(period="1d", interval="15m")
            
            if not df.empty:
                current_price = df['Close'].iloc[-1]
                log(f"📊 السعر الحالي: {current_price:.2f}")
                
                # التحليل باستخدام SMC
                prompt = f"Analyze Gold using Smart Money Concepts (SMC) for the current price {current_price:.2f}. Provide a clear 'Entry' or 'Wait' signal."
                response = ai_model.generate_content(prompt)
                
                # فحص الرد وإرساله
                if any(word in response.text.lower() for word in ["دخول", "target", "entry", "🎯", "buy", "sell"]):
                    bot.send_message(chat_id, f"🎯 إشارة ذهب (SMC):\n{response.text}")
                    log("📩 تم إرسال الإشارة للتليجرام")
            
            # انتظر 5 دقائق قبل الفحص التالي
            time.sleep(300) 
            
        except Exception as e:
            log(f"❌ خطأ في الدورة: {e}")
            time.sleep(60)

@app.route('/')
def home():
    return "Aurum-Signals Bot is running!", 200

if __name__ == "__main__":
    # تشغيل خيط المراقبة في الخلفية
    monitor_thread = threading.Thread(target=background_monitor)
    monitor_thread.daemon = True
    monitor_thread.start()
    
    # تشغيل السيرفر
    port = int(os.environ.get("PORT", 10000))
    log(f"🚀 السيرفر شغال على بورت {port}")
    try:
        serve(app, host='0.0.0.0', port=port)
    except Exception as e:
        log(f"💥 فشل السيرفر: {e}")
        
