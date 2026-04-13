import os
import yfinance as yf
import telebot
import google.generativeai as genai
import time
from flask import Flask
from threading import Thread

# --- 1. إعداد السيرفر الوهمي (Keep-Alive) ---
app = Flask('')

@app.route('/')
def home():
    return "🎯 Gold Sniper Bot is Online and Active!"

def run_web_server():
    # تشغيل السيرفر على المنفذ المطلوب من Render
    app.run(host='0.0.0.0', port=10000)

# --- 2. إعداد المفاتيح والذكاء الاصطناعي ---
GEMINI_KEY = os.environ.get('GEMINI_KEY')
TELE_TOKEN = os.environ.get('TELE_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')

genai.configure(api_key=GEMINI_KEY)
ai_model = genai.GenerativeModel('gemini-1.5-flash')
bot = telebot.TeleBot(TELE_TOKEN)

# --- 3. منطق الاستراتيجية والتحليل ---
def get_sniper_signal():
    try:
        # جلب بيانات الذهب 15 دقيقة
        gold = yf.Ticker("GC=F")
        df_15m = gold.history(period="2d", interval="15m")
        
        if df_15m.empty:
            return "تعذر جلب البيانات"

        current_price = df_15m['Close'].iloc[-1]
        
        # البرومبت الاحترافي لتحليل SMC
        prompt = (
            f"سعر الذهب الحالي: {current_price:.2f}. "
            "قم بتحليل السوق بناءً على مفاهيم الأموال الذكية (SMC)، "
            "ابحث عن مناطق العرض والطلب (Supply/Demand) وكسر الهيكل (MS) ومؤشر RSI. "
            "إذا وجدت فرصة دخول قوية، أرسل: نقطة الدخول، الأهداف (TP)، ووقف الخسارة (SL). "
            "إذا كان السوق متذبذب، قل: 'لا توجد إشارة واضحة حالياً'. "
            "اجعل الرد باللغة العربية حصراً."
        )
        
        response = ai_model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"خطأ تقني: {str(e)}"

# --- 4. الدالة الأساسية لتشغيل البوت ---
def start_bot_logic():
    print("🎯 بدء تشغيل محرك البوت...")
    
    # رسالة ترحيبية فورية عند التشغيل (للتأكد من الربط)
    try:
        bot.send_message(CHAT_ID, "🚀 القناص استيقظ! تم الربط بنجاح وأنا الآن أراقب سوق الذهب (XAU/USD) لحظة بلحظة.")
        print("✅ تم إرسال رسالة الترحيب بنجاح.")
    except Exception as e:
        print(f"❌ خطأ في إرسال رسالة الترحيب: {e}")

    # حلقة الفحص المستمر
    while True:
        print("🔍 جاري فحص السوق بحثاً عن قناصات...")
        signal = get_sniper_signal()
        
        # لا نرسل رسالة إلا إذا كان هناك تحليل حقيقي يحتوي على "دخول" أو "هدف"
        if "دخول" in signal or "نقطة" in signal or "هدف" in signal:
            bot.send_message(CHAT_ID, f"🎯 إشارة ذهب جديدة:\n\n{signal}")
            print("📩 تم إرسال إشارة جديدة لتليجرام.")
        else:
            print("😴 لا توجد فرصة دخول قوية في الوقت الحالي.")

        # الانتظار 15 دقيقة
        time.sleep(900)

# --- 5. نقطة الانطلاق ---
if __name__ == "__main__":
    # تشغيل محرك البوت في مسار (Thread) منفصل
    bot_thread = Thread(target=start_bot_logic)
    bot_thread.start()
    
    # تشغيل السيرفر الوهمي في المسار الرئيسي
    print("🌐 تشغيل السيرفر الوهمي للعمل 24/7...")
    run_web_server()
