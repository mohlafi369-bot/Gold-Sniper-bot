import yfinance as yf
import telebot
import google.generativeai as genai
import time

# إعداداتك (تأكد من وضع قيمك الصحيحة)
GEMINI_KEY = "AIzaSyDCrJQi4V2vKzsN2pXFnUsFHwJUhaKpSek"
TELE_TOKEN = "8511972416:AAGIKxSzx8Sh39Ty58JnpajHazXKgqmUsgM"
CHAT_ID = "834853809"

genai.configure(api_key=GEMINI_KEY)
ai_model = genai.GenerativeModel('gemini-1.5-flash')
bot = telebot.TeleBot(TELE_TOKEN)

def get_sniper_signal():
    gold = yf.Ticker("GC=F")
    # جلب بيانات فريم الساعة للاتجاه و 15 دقيقة للتنفيذ
    df_1h = gold.history(period="2d", interval="1h")
    df_15m = gold.history(period="1d", interval="15m")
    
    current_price = df_15m['Close'].iloc[-1]
    
    # حساب مؤشر بسيط RSI (تقريبي) للفلترة
    delta = df_15m['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs.iloc[-1]))

    # --- منطق القناص ---
    # لا نرسل للذكاء الاصطناعي إلا إذا كان هناك "تطرف" في السعر (RSI > 70 أو < 30)
    if rsi < 35 or rsi > 65:
        prompt = f"""
        تحليل ذهب XAU/USD (نظام القناص):
        السعر: {current_price:.2f}, RSI: {rsi:.2f}
        بناءً على مناطق العرض والطلب (SMC) والسيولة:
        1. هل هناك فرصة دخول قوية؟
        2. إذا نعم، أعطني: (نوع الصفقة، دخول، هدف، وقف خسارة صامد).
        اجعل الرد بصيغة إشارة تداول مختصرة واحترافية.
        """
        response = ai_model.generate_content(prompt)
        return response.text
    return None

print("🎯 نظام القناص يعمل الآن بصمت...")

while True:
    try:
        signal = get_sniper_signal()
        if signal:
            bot.send_message(CHAT_ID, f"🎯 **إشارة قناص جديدة** 🎯\n\n{signal}", parse_mode="Markdown")
            time.sleep(3600) # إذا أرسل إشارة، انتظر ساعة قبل البحث عن أخرى لضمان الجودة
        else:
            print("الأسعار مستقرة، لا توجد فرص قناص حالياً...")
            time.sleep(300) # افحص كل 5 دقائق بصمت
    except Exception as e:
        print(f"Error: {e}")
        time.sleep(60)
