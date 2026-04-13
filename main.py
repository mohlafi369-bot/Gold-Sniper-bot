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
    log(f"❌ خطأ في تحميل المكتبات: {e}")

app = Flask('')

def background_monitor():
    log("📡 بدأت المراقبة...")
    
    while True:
        try:
            # جلب المتغيرات من Render
            api_key = os.environ.get('GOOGLE_API_KEY')
            tele_token = os.environ.get('TELE_TOKEN')
            chat_id = os.environ.get('CHAT_ID')

            # فحص تشخيصي للمفاتيح
            if not api_key or not tele_token or not chat_id:
                missing = []
                if not api_key: missing.append("GOOGLE_API_KEY")
                if not tele_token: missing.append("TELE_TOKEN")
                if not chat_id: missing.append("CHAT_ID")
                log(f"⚠️ نقص في المتغيرات: {', '.join(missing)}")
                time.sleep(20)
                continue

            # إعداد Gemini و Bot
            genai.configure(api_key=api_key)
            ai_model = genai.GenerativeModel('gemini-1.5-flash')
            bot = telebot.TeleBot(tele_token)
            
            # جلب بيانات الذهب (Gold Spot)
            gold = yf.Ticker("GC=F")
            df = gold.history(period="1d", interval="15m")
            
            if not df.empty:
                current_price = df['Close'].iloc[-1]
                log(f"📊 السعر الحالي: {current_price:.2f}")
                
                # تحسين الـ Prompt ليكون أكثر احترافية في الـ SMC
                prompt = (
                    f"Analyze Gold (XAU/USD) at price {current_price:.2f} using Smart Money Concepts (SMC). "
                    "Look for Break of Structure (BOS) or Order Blocks. "
                    "Give a clear 'Entry', 'Target', and 'Stop Loss' or say 'Wait for setup'."
                )
                
                response = ai_model.generate_content(prompt)
                analysis_text = response.text
                
                # إرسال الرسالة إذا وجد إشارة دخول
                keywords = ["entry", "target", "buy", "sell", "دخول", "🎯", "order block"]
                if any(word in analysis_text.lower() for word in keywords):
                    message = f"🌟 **Gold Signal (SMC)**\n\n{analysis_text}\n\n💰 Price: {current_price:.2f}"
                    bot.send_message(chat_id, message)
                    log("📩 تم إرسال الإشارة إلى تليجرام بنجاح")
                else:
                    log("💤 التحليل: انتظار فرصة أفضل (No Entry)")
            
            # فحص كل 5 دقائق
            time.sleep(300) 
            
        except Exception as e:
            log(f"❌ خطأ أثناء التشغيل: {e}")
            time.sleep(60)

@app.route('/')
def home():
    return "Aurum-Signals is Online", 200

if __name__ == "__main__":
    # تشغيل خيط المراقبة
    monitor_thread = threading.Thread(target=background_monitor)
    monitor_thread.daemon = True
    monitor_thread.start()
    
    # تشغيل السيرفر لضمان بقاء Render نشطاً
    port = int(os.environ.get("PORT", 10000))
    log(f"🚀 السيرفر يعمل على بورت {port}")
    try:
        serve(app, host='0.0.0.0', port=port)
    except Exception as e:
        log(f"💥 فشل في تشغيل السيرفر: {e}")
