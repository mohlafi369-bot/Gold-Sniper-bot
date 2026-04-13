import os
import yfinance as yf
import telebot
import google.generativeai as genai
import time
from flask import Flask

app = Flask('')

# --- الإعدادات ---
GEMINI_KEY = os.environ.get('GEMINI_KEY')
TELE_TOKEN = os.environ.get('TELE_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')

genai.configure(api_key=GEMINI_KEY)
ai_model = genai.GenerativeModel('gemini-1.5-flash')
bot = telebot.TeleBot(TELE_TOKEN)

# دالة الفحص (نفس استراتيجيتك القوية)
def check_gold_market():
    try:
        gold = yf.Ticker("GC=F")
        df = gold.history(period="2d", interval="15m")
        if df.empty: return "لا توجد بيانات"
        
        current_price = df['Close'].iloc[-1]
        prompt = (f"السعر: {current_price:.2f}. حلل بنظام SMC و RSI. "
                  "إذا وجدت صفقة قوية (دخول، هدف، وقف) اذكرها، وإلا قل 'انتظار'. بالعربية.")
        
        response = ai_model.generate_content(prompt)
        res_text = response.text
        
        print(f"🔍 نتيجة التحليل: {res_text[:30]}...")
        
        if any(word in res_text for word in ["دخول", "نقطة", "هدف"]):
            bot.send_message(CHAT_ID, f"🎯 إشارة قناص جديدة:\n\n{res_text}")
            return "SIGNAL_SENT"
        return "NO_SIGNAL"
    except Exception as e:
        print(f"❌ خطأ فحص: {e}")
        return str(e)

# --- المسار الرئيسي (كل زيارة من Cron-job تشغل هذا الكود) ---
@app.route('/')
def home():
    current_time = time.strftime("%H:%M:%S", time.localtime())
    print(f"🕒 تم استلام نبض من Cron-job الساعة {current_time}")
    
    # تشغيل الفحص فوراً عند كل زيارة
    status = check_gold_market()
    
    return f"Bot is Active. Last check: {current_time}. Status: {status}", 200

if __name__ == "__main__":
    # إرسال رسالة تشغيل لمرة واحدة
    try:
        bot.send_message(CHAT_ID, "🚀 القناص استيقظ بنظام (On-Demand)!")
    except: pass
    
    print("🌐 السيرفر يعمل بنظام الاستجابة الفورية...")
    app.run(host='0.0.0.0', port=10000)
    
