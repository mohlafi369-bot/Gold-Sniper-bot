import os
import sys
import time

# دالة لضمان ظهور اللوجز فوراً
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

# إعداد الذكاء الاصطناعي
try:
    genai.configure(api_key=GEMINI_KEY)
    ai_model = genai.GenerativeModel('gemini-1.5-flash')
    bot = telebot.TeleBot(TELE_TOKEN)
    log("✅ تم إعداد Gemini و Telegram بنجاح")
except Exception as e:
    log(f"❌ خطأ في الإعدادات: {e}")

@app.route('/')
def home():
    try:
        log("🔍 مستخدم دخل للرابط.. بدء فحص الذهب")
        gold = yf.Ticker("GC=F")
        df = gold.history(period="1d", interval="15m")
        if df.empty:
            return "بيانات الذهب غير متوفرة حالياً", 200
            
        current_price = df['Close'].iloc[-1]
        
        prompt = f"حلل الذهب SMC للسعر {current_price:.2f}. أعطِ توصية دخول قوية فقط أو قل انتظار."
        response = ai_model.generate_content(prompt)
        res_text = response.text
        
        if any(word in res_text for word in ["دخول", "هدف", "نقطة"]):
            bot.send_message(CHAT_ID, f"🎯 إشارة ذهب:\n\n{res_text}")
            log("📩 تم إرسال إشارة لتليجرام")
            
        return f"Bot is LIVE. Price: {current_price} | Status: {res_text[:20]}...", 200
    except Exception as e:
        log(f"❌ خطأ أثناء الفحص: {e}")
        return f"Error: {str(e)}", 500

if __name__ == "__main__":
    log("🚀 تشغيل السيرفر الاحترافي على Port 10000...")
    try:
        # إرسال رسالة تجريبية فورية للتأكد من الاتصال
        bot.send_message(CHAT_ID, "🚀 القناص استيقظ الآن! جرب فتح الرابط يدوياً.")
        serve(app, host='0.0.0.0', port=10000)
    except Exception as e:
        log(f"💥 فشل تشغيل السيرفر: {e}")
        
