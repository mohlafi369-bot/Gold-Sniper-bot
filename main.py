import os
import yfinance as yf
import telebot
import google.generativeai as genai
import time
from flask import Flask
from threading import Thread

# --- 1. إعداد السيرفر (خفيف جداً لضمان النجاح) ---
app = Flask('')

@app.route('/')
def home():
    # رد بسيط جداً لمنع خطأ Output too large في Cron-job
    return "OK", 200

def run_web_server():
    # تشغيل السيرفر على المنفذ المخصص
    app.run(host='0.0.0.0', port=10000)

# --- 2. إعداد المفاتيح والذكاء الاصطناعي ---
GEMINI_KEY = os.environ.get('GEMINI_KEY')
TELE_TOKEN = os.environ.get('TELE_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')

genai.configure(api_key=GEMINI_KEY)
ai_model = genai.GenerativeModel('gemini-1.5-flash')
bot = telebot.TeleBot(TELE_TOKEN)

# --- 3. استراتيجية القناص الاحترافية (SMC) ---
def get_sniper_signal():
    try:
        # جلب بيانات الذهب بدقة 15 دقيقة
        gold = yf.Ticker("GC=F")
        df = gold.history(period="2d", interval="15m")
        
        if df.empty:
            return "انتظار"

        current_price = df['Close'].iloc[-1]
        
        # البرومبت المطور لاستخراج صفقات عالية الجودة
        prompt = (
            f"السعر الحالي للذهب: {current_price:.2f}. "
            "حلل السوق باستخدام مفاهيم الأموال الذكية (SMC): "
            "1. حدد مناطق السيولة (Liquidity) وكسر الهيكل (MSB). "
            "2. ابحث عن مناطق العرض والطلب القوية (Supply/Demand). "
            "3. ادمج مؤشر RSI لتحديد التشبع. "
            "إذا كانت هناك فرصة دخول واضحة، أرسل: نقطة الدخول، الأهداف (TP)، ووقف الخسارة (SL). "
            "إذا لم تكن هناك فرصة، ابدأ ردك بكلمة 'انتظار'. "
            "اجعل التحليل باللغة العربية ومختصراً."
        )
        
        response = ai_model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"خطأ في التحليل: {str(e)}"

# --- 4. محرك البوت الأساسي ---
def start_bot_logic():
    # انتظار بسيط لضمان استقرار السيرفر عند البدء
    time.sleep(10)
    print("🎯 محرك القناص بدأ العمل الآن...")
    
    try:
        bot.send_message(CHAT_ID, "🚀 القناص استيقظ! نظام الـ SMC مفعل الآن ومراقب للذهب 24/7.")
    except Exception as e:
        print(f"❌ فشل إرسال رسالة الترحيب: {e}")

    last_check_time = 0
    
    while True:
        current_now = time.time()
        readable_time = time.strftime("%H:%M:%S", time.localtime())
        
        # طباعة نبض الحياة في اللوجز كل دقيقة (للاطمئنان)
        print(f"💓 نبض البوت: {readable_time} - السيرفر مستقر.")

        # فحص السوق كل 15 دقيقة (900 ثانية)
        if current_now - last_check_time >= 900:
            print("🔍 جاري فحص الذهب بحثاً عن قناصات...")
            signal = get_sniper_signal()
            
            # طباعة جزء من التحليل في اللوجز للتأكد من عمل Gemini
            print(f"🤖 نتيجة الفحص: {signal[:40]}...")

            # إرسال الرسالة فقط إذا كانت تحتوي على إشارة دخول حقيقية
            if "دخول" in signal or "نقطة" in signal or "هدف" in signal:
                bot.send_message(CHAT_ID, f"🎯 إشارة ذهب جديدة:\n\n{signal}")
                print("📩 تم إرسال إشارة قوية لتليجرام!")
            
            last_check_time = current_now
        
        # الانتظار لمدة دقيقة قبل طباعة النبض القادم
        time.sleep(60)

# --- 5. التشغيل النهائي ---
if __name__ == "__main__":
    # تشغيل منطق التداول في Thread منفصل (Daemon لضمان الاستمرارية)
    bot_thread = Thread(target=start_bot_logic, daemon=True)
    bot_thread.start()
    
    # تشغيل السيرفر في المسار الرئيسي
    print("🌐 تشغيل نظام الاستضافة المستمرة...")
    run_web_server()
    
