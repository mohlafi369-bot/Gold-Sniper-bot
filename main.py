import os
import yfinance as yf
import telebot
from google import genai
import time
import sys
from flask import Flask
from waitress import serve

app = Flask('')

# --- الإعدادات ---
GEMINI_KEY = os.environ.get('GEMINI_KEY')
TELE_TOKEN = os.environ.get('TELE_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')

client = genai.Client(api_key=GEMINI_KEY)
bot = telebot.TeleBot(TELE_TOKEN)

def check_gold_market():
    try:
        # جلب البيانات
        gold = yf.Ticker("GC=F")
        df = gold.history(period="1d", interval="15m")
        if df.empty: return "بيانات Yahoo Finance فارغة حالياً"
        
        current_price = df['Close'].iloc[-1]
        
        # استخدام المكتبة الجديدة google-genai
        prompt = (f"سعر الذهب: {current_price:.2f}. حلل بنظام SMC (الأموال الذكية). "
                  "إذا وجد دخول قوي (دخول، هدف، وقف) اذكره، وإلا قل 'انتظار'.")
        
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt
        )
        res_text = response.text
        
        # إرسال النتيجة لتليجرام
        if any(word in res_text for word in ["دخول", "نقطة", "هدف"]):
            bot.send_message(CHAT_ID, f"🎯 قناص الذهب:\n\n{res_text}")
            return "SUCCESS: SIGNAL SENT"
        return f"NO SIGNAL (Price: {current_price})"
        
    except Exception as e:
        error_msg = f"❌ خطأ فني: {str(e)}"
        print(error_msg, flush=True)
        # إرسال الخطأ لتليجرام لتعرف ما المشكلة فوراً
        try: bot.send_message(CHAT_ID, error_msg)
        except: pass
        return error_msg

@app.route('/')
def home():
    t = time.strftime("%H:%M:%S", time.localtime())
    print(f"🕒 زيارة جديدة للرابط الساعة {t}", flush=True)
    
    # تنفيذ الفحص
    status = check_gold_market()
    
    return f"Status: {status} | Time: {t}", 200

if __name__ == "__main__":
    print("🚀 بدء تشغيل السيرفر الاحترافي...", flush=True)
    # إشعار تشغيل
    try: bot.send_message(CHAT_ID, "🚀 القناص استيقظ بنسخة 2.0 المحدثة!")
    except: pass
    
    serve(app, host='0.0.0.0', port=10000)
    
