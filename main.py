import os
import yfinance as yf
import telebot
import google.generativeai as genai
import time
from flask import Flask
from threading import Thread

# --- 1. سيرفر خفيف جداً لإرضاء Cron-job ---
app = Flask('')

@app.route('/')
def home():
    # نص قصير جداً لتجنب خطأ "Output too large"
    return "OK", 200

def run_web_server():
    app.run(host='0.0.0.0', port=10000)

# --- 2. الإعدادات ---
GEMINI_KEY = os.environ.get('GEMINI_KEY')
TELE_TOKEN = os.environ.get('TELE_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')

genai.configure(api_key=GEMINI_KEY)
ai_model = genai.GenerativeModel('gemini-1.5-flash')
bot = telebot.TeleBot(TELE_TOKEN)

# --- 3. منطق التحليل ---
def get_sniper_signal():
    try:
        gold = yf.Ticker("GC=F")
        df_15m = gold.history(period="2d", interval="15m")
        if df_15m.empty: return "لا توجد بيانات"
        
        current_price = df_15m['Close'].iloc[-1]
        prompt = (f"السعر: {current_price:.2f}. حلل بنظام SMC و RSI. "
                  "إذا وجدت صفقة قوية أعطني: دخول، هدف، وقف. "
                  "إذا لا، قل 'انتظار'. بالعربية.")
        
        response = ai_model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"خطأ: {e}"

# --- 4. تشغيل المحرك ---
def start_bot_logic():
    print("🎯 المحرك بدأ العمل...")
    # إرسال رسالة لمرة واحدة عند التشغيل للتأكد
    try:
        bot.send_message(CHAT_ID, "🚀 البوت استيقظ والربط سليم!")
    except: pass

    last_check = 0
    while True:
        current_now = time.time()
        
        # طباعة "نبض" كل دقيقة في اللوجز لتطمئن
        t_str = time.strftime("%H:%M:%S", time.localtime())
        print(f"💓 نبض البوت: شغال تمام الساعة {t_str}")

        # فحص السوق كل 15 دقيقة (900 ثانية)
        if current_now - last_check > 900:
            print("🔍 فحص السوق الآن...")
            signal = get_sniper_signal()
            print(f"📝 النتيجة: {signal[:30]}...")
            
            if any(word in signal for word in ["دخول", "نقطة", "هدف"]):
                bot.send_message(CHAT_ID, f"🎯 إشارة جديدة:\n\n{signal}")
            
            last_check = current_now
        
        time.sleep(60) # ينام دقيقة ويعيد طباعة النبض

if __name__ == "__main__":
    Thread(target=start_bot_logic).start()
    run_web_server()
    
