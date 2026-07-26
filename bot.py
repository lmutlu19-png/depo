
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import yfinance as yf


TOKEN = "8775658684:AAHCX0b2fxMgDca_yTUgFR4S7XAgTpA8X6s"

CHAT_ID = "6009849892"


portfoy = {
    "ALTNY": {"adet": 21874, "maliyet": 17.07},
    "ARFYE": {"adet": 4000, "maliyet": 29.32},
    "BRLSM": {"adet": 10000, "maliyet": 19.19},
    "CATES": {"adet": 2000, "maliyet": 43.28},
    "NETCD": {"adet": 1050, "maliyet": 148.25},
    "SILVR": {"adet": 27500, "maliyet": 2.91},
    "TUCLK": {"adet": 8000, "maliyet": 4.63},
    "YIGIT": {"adet": 5000, "maliyet": 23.76}
}


son_sinyal = {}

alarm_aktif = True



def veri_getir(hisse):

    try:
        df = yf.Ticker(hisse + ".IS").history(period="6mo")
        return df

    except:
        return None



def analiz(hisse):

    df = veri_getir(hisse)

    if df is None or len(df) < 20:
        return None


    df["EMA5"] = df["Close"].ewm(span=5).mean()
    df["EMA8"] = df["Close"].ewm(span=8).mean()
    df["EMA13"] = df["Close"].ewm(span=13).mean()


    fiyat = df["Close"].iloc[-1]

    hacim = df["Volume"].iloc[-1]
    ort_hacim = df["Volume"].tail(20).mean()


    ema5 = df["EMA5"].iloc[-1]
    ema8 = df["EMA8"].iloc[-1]
    ema13 = df["EMA13"].iloc[-1]


    if ema5 > ema8 and ema8 > ema13 and hacim > ort_hacim:

        durum = "🟢 GÜÇLÜ AL"

    elif ema5 > ema8:

        durum = "🟡 TAKİP"

    else:

        durum = "🔴 ZAYIF"



    return {
        "fiyat": round(float(fiyat),2),
        "ema5": round(float(ema5),2),
        "ema8": round(float(ema8),2),
        "ema13": round(float(ema13),2),
        "hacim": "YÜKSEK" if hacim > ort_hacim else "NORMAL",
        "durum": durum
    }



def canli_fiyat(hisse):

    sonuc = analiz(hisse)

    if sonuc:
        return sonuc["fiyat"]

    return 0
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "✅ LeventBorBot aktif\n\n"
        "/portfoy\n"
        "/fiyat\n"
        "/durum\n"
        "/trend\n"
        "/karar\n"
        "/gunluk\n"
        "/alarm_ac\n"
        "/alarm_kapat"
    )



async def portfoy_liste(update: Update, context: ContextTypes.DEFAULT_TYPE):

    mesaj = "📊 LEVENT PORTFÖY\n\n"

    for hisse, bilgi in portfoy.items():

        mesaj += (
            f"{hisse}\n"
            f"Adet: {bilgi['adet']}\n"
            f"Maliyet: {bilgi['maliyet']} TL\n\n"
        )

    await update.message.reply_text(mesaj)



async def fiyat(update: Update, context: ContextTypes.DEFAULT_TYPE):

    mesaj = "📈 CANLI FİYATLAR\n\n"

    for hisse in portfoy:

        mesaj += f"{hisse}: {canli_fiyat(hisse)} TL\n"

    await update.message.reply_text(mesaj)



async def trend(update: Update, context: ContextTypes.DEFAULT_TYPE):

    mesaj = "📈 5-8-13 + HACİM ANALİZ\n\n"

    for hisse in portfoy:

        sonuc = analiz(hisse)

        if sonuc:

            mesaj += (
                f"📌 {hisse}\n"
                f"Fiyat: {sonuc['fiyat']}\n"
                f"EMA5: {sonuc['ema5']}\n"
                f"EMA8: {sonuc['ema8']}\n"
                f"EMA13: {sonuc['ema13']}\n"
                f"Hacim: {sonuc['hacim']}\n"
                f"{sonuc['durum']}\n\n"
            )

    await update.message.reply_text(mesaj)



async def alarm_ac(update: Update, context: ContextTypes.DEFAULT_TYPE):

    global alarm_aktif

    alarm_aktif = True

    await update.message.reply_text(
        "🔔 Alarm bildirimleri AÇILDI"
    )



async def alarm_kapat(update: Update, context: ContextTypes.DEFAULT_TYPE):

    global alarm_aktif

    alarm_aktif = False

    await update.message.reply_text(
        "🔕 Alarm bildirimleri KAPATILDI"
    )



async def alarm_kontrol(context: ContextTypes.DEFAULT_TYPE):

    if not alarm_aktif:
        return


    for hisse in portfoy:

        sonuc = analiz(hisse)

        if sonuc:

            yeni = sonuc["durum"]
            eski = son_sinyal.get(hisse)


            if yeni != eski:

                await context.bot.send_message(
                    chat_id=CHAT_ID,
                    text=(
                        f"🔔 TREND DEĞİŞİMİ\n\n"
                        f"📌 {hisse}\n"
                        f"Yeni: {yeni}\n"
                        f"Fiyat: {sonuc['fiyat']}\n"
                        f"EMA5: {sonuc['ema5']}\n"
                        f"EMA8: {sonuc['ema8']}\n"
                        f"EMA13: {sonuc['ema13']}\n"
                        f"Hacim: {sonuc['hacim']}"
                    )
                )

                son_sinyal[hisse] = yeni
app = Application.builder().token(TOKEN).build()


app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("portfoy", portfoy_liste))
app.add_handler(CommandHandler("fiyat", fiyat))
app.add_handler(CommandHandler("trend", trend))
app.add_handler(CommandHandler("alarm_ac", alarm_ac))
app.add_handler(CommandHandler("alarm_kapat", alarm_kapat))


app.job_queue.run_repeating(
    alarm_kontrol,
    interval=3600,
    first=10
)


print("🚀 LeventBorBot çalışıyor...")


app.run_polling()