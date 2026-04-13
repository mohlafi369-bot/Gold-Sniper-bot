import os
import yfinance as yf
import telebot
import google.generativeai as genai
import time
from flask import Flask
from threading import Thread

# --- 1. إعداد السيرفر الوهمي (للبقاء مجانياً على Render) ---
app = Flask('')

@app.route('/')
def home():
    return "🎯 Gold Sniper Bot is Online!"

def run():
    # Render يستخدم المنفذ 10000 تلقائياً
    app.run(host='0.0.0.0', port=10000)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- 2. إعداد المفاتيح من البيئة (Environment Variables) ---
GEMINI_KEY = os.environ.get('GEMINI_KEY')
TELE_TOKEN = os.environ.get('TELE_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')

# إعداد الذكاء الاصطناعي وتليجرام
genai.configure(api_key=GEMINI_KEY)
ai_model = genai.GenerativeModel('gemini-1.5-flash')
bot = telebot.TeleBot(TELE_TOKEN)

# --- 3. منطق تحليل الذهب وإرسال الإشارات ---
def get_sniper_signal():
    try:
        # جلب بيانات الذهب (عقود نيويورك الآجلة)
        gold = yf.Ticker("GC=F")
        df_15m = gold.history(period="2d", interval="15m")
        
        if df_15m.empty:
            return "تعذر جلب بيانات السعر حالياً."

        current_price = df_15m['Close'].iloc[-1]
        
        # البرومبت المخصص للتحليل بنظام SMC
        prompt = (
            f"Current Gold Price: {current_price:.2f}. "
            "Analyze the market using Smart Money Concepts (SMC), Order Blocks, and RSI. "
            "If there is a high-probability trade, provide: Entry, TP, and SL. "
            "If the market is sideways, say: 'No clear signal, waiting for liquidity'."
            "Reply in Arabic."
        )
        
        response = ai_model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"خطأ في التحليل: {str(e)}"

# --- 4. تشغيل البوت ---
if __name__ == "__main__":
    # تشغيل السيرفر في الخلفية
    keep_alive()
    
    print("🎯 جاري تشغيل البوت...")
    
    # إرسال رسالة ترحيبية فورية لتأكيد الربط
    try:
        bot.send_message(CHAT_ID, "🚀 القناص استيقظ! أنا الآن متصل وأراقب الذهب (XAU/USD) على مدار الساعة.")
    except Exception as e:
        print(f"خطأ في إرسال رسالة الترحيب: {e}")

    # حلقة الفحص المستمر
    while True:
        print("🔍 فحص السوق الآن...")
        signal = get_sniper_signal()
        
        # إرسال الإشارة فقط إذا كانت تحتوي على صفقة (تجنب الإزعاج)
        if "دخول" in signal or "Entry" in signal or "هدف" in signal:
            bot.send_message(CHAT_ID, f"🎯 إشارة قناص جديدة:\n\n{signal}")
        else:
            print("😴 لا توجد إشارة قوية حالياً.")

        # الانتظار لمدة 15 دقيقة قبل الفحص التالي
        time.sleep(900)
        
