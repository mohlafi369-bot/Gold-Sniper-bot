import os
import yfinance as yf
import telebot
import google.generativeai as genai
import time
from flask import Flask
from waitress import serve # استدعاء السيرفر الاحترافي

app = Flask('')

# --- الإعدادات ---
GEMINI_KEY = os.environ.get('GEMINI_KEY')
TELE_TOKEN = os.environ.get('TELE_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')

genai.configure(api_key=GEMINI_KEY)
ai_model = genai.GenerativeModel('gemini-1.5-flash')
bot = telebot.TeleBot(TELE_TOKEN)

def check_gold_market():
    try:
        gold = yf.Ticker("GC=F")
        df = gold.history(period="2d", interval="15m")
        if df.empty: return "بيانات فارغة"
        
        current_price = df['Close'].iloc[-1]
        prompt = (f"السعر: {current_price:.2f}. حلل SMC و RSI. "
                  "إذا وجد دخول قوي (دخول، هدف، وقف) أرسله، وإلا قل 'انتظار'.")
        
        response = ai_model.generate_content(prompt)
        res_text = response.text
        
        if any(word in res_text for word in ["دخول", "نقطة", "هدف"]):
            bot.send_message(CHAT_ID, f"🎯 إشارة قوية:\n\n{res_text}")
            return "SUCCESS_SIGNAL"
        return "NO_SIGNAL"
    except Exception as e:
        return f"ERROR: {e}"

@app.route('/')
def home():
    # عند كل زيارة من Cron-job، نقوم بالفحص
    t = time.strftime("%H:%M:%S", time.localtime())
    status = check_gold_market()
    print(f"✅ تم النبض والفحص بنجاح الساعة {t} | الحالة: {status}")
    return f"Bot Active - {t}", 200

if __name__ == "__main__":
    # رسالة ترحيبية فورية
    try:
        bot.send_message(CHAT_ID, "🚀 القناص استيقظ بنظام الاستجابة الاحترافي (Waitress)!")
    except: pass
    
    # تشغيل السيرفر باستخدام waitress لضمان استقرار البورت في Render
    print("🌐 السيرفر الاحترافي يعمل الآن على المنفذ 10000...")
    serve(app, host='0.0.0.0', port=10000)
    
