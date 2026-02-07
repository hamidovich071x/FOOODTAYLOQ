from flask import Flask, request, redirect, send_file
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import io, requests

app = Flask(__name__)
app.secret_key = "taylaqfood"

# ================= TELEGRAM =================
TELEGRAM_TOKEN = "8532829799:AAHp4rZ43UUGjuvrDBPFA5LFKW_OENnP9ds"
CHAT_ID = "8435898042"

def send_to_telegram(text):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": text}, timeout=5)
    except:
        pass

# ================= DATA =================
ADMIN_PASSWORD = "1234"
orders = []

menu = {
    "Osh": {"price": 25000, "img": "https://images.unsplash.com/photo-1604908177522-0409cfe7c36d"},
    "Lag‘mon": {"price": 30000, "img": "https://images.unsplash.com/photo-1625944525533-473f1a3f87b5"},
    "Manti": {"price": 28000, "img": "https://images.unsplash.com/photo-1626078292169-35d6a8b5f9e4"},
}

fast_food = {
    "Burger": {"price": 30000, "img": "https://images.unsplash.com/photo-1550547660-d9450f859349"},
    "Pizza": {"price": 45000, "img": "https://images.unsplash.com/photo-1548365328-8b849e6e3b45"},
}

drinks = {
    "Cola": {"price": 10000, "img": "https://images.unsplash.com/photo-1629203851122-3726ecdf080e"},
    "Choy": {"price": 5000, "img": "https://images.unsplash.com/photo-1544787219-7f47ccb76574"},
}

cart = []

# ================= UI =================
def page(title, body):
    return f"""<!DOCTYPE html>
<html lang="uz">
<head>
<meta charset="UTF-8">
<title>{title}</title>
<style>
*{{box-sizing:border-box}}
body{{margin:0;font-family:Segoe UI,sans-serif;background:#0e0e0e;color:#fff}}
header{{background:#000;padding:25px 40px;display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #222}}
nav a{{color:#aaa;margin-left:20px;text-decoration:none}}
nav a:hover{{color:#fff}}
.container{{padding:40px;display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:30px}}
.card{{background:#151515;border-radius:18px;overflow:hidden;border:1px solid #222}}
.card img{{width:100%;height:200px;object-fit:cover}}
.btn{{display:inline-block;margin:15px;padding:12px 18px;background:#fff;color:#000;border-radius:30px;text-decoration:none}}
.box{{max-width:520px;margin:50px auto;background:#151515;padding:30px;border-radius:20px;border:1px solid #222}}
input,textarea{{width:100%;padding:12px;margin:10px 0;border-radius:10px;border:none;background:#222;color:#fff}}
footer{{text-align:center;padding:25px;color:#555;border-top:1px solid #222}}
</style>
</head>
<body>
<header>
<h1>TAYLAQ</h1>
<nav>
<a href="/">Bosh sahifa</a>
<a href="/fast">Fast Food</a>
<a href="/drinks">Ichimliklar</a>
<a href="/cart">Savat</a>
<a href="/contact">Aloqa</a>
<a href="/admin">Admin</a>
</nav>
</header>
{body}
<footer>© 2026 Taylaq Food</footer>
</body>
</html>"""

def cards(data):
    h="<div class='container'>"
    for n,i in data.items():
        h+=f"""
        <div class="card">
        <img src="{i['img']}">
        <h3 style="margin:15px">{n}</h3>
        <p style="margin:0 15px 15px">{i['price']} so'm</p>
        <a class="btn" href="/add/{n}">Savatga</a>
        </div>"""
    return h+"</div>"

def price_of(n):
    for c in (menu, fast_food, drinks):
        if n in c:
            return c[n]["price"]
    return 0

# ================= ROUTES =================
@app.route("/")
def home():
    return page("Bosh sahifa", cards(menu))

@app.route("/fast")
def fast():
    return page("Fast Food", cards(fast_food))

@app.route("/drinks")
def drink():
    return page("Ichimliklar", cards(drinks))

@app.route("/add/<n>")
def add(n):
    if price_of(n) > 0:
        cart.append(n)
    return redirect(request.referrer or "/")

@app.route("/cart")
def cart_page():
    total = sum(price_of(i) for i in cart)
    items = "".join(f"<p>• {i} — {price_of(i)} so'm</p>" for i in cart) or "<p>Savat bo‘sh</p>"
    return page("Savat", f"""
    <div class="box">
    {items}<hr>
    <h3>Jami: {total} so'm</h3>
    <a class="btn" href="/payment">To‘lov</a>
    </div>""")

@app.route("/payment", methods=["GET","POST"])
def payment():
    if request.method == "POST" and cart:
        total = sum(price_of(i) for i in cart)

        text = "🍽 YANGI BUYURTMA\n\n"
        for i in cart:
            text += f"• {i} — {price_of(i)} so'm\n"
        text += f"\n💰 Jami: {total} so'm"

        send_to_telegram(text)

        orders.append({"items": cart.copy(), "total": total})
        cart.clear()

        return page("OK","<div class='box'><h2>Buyurtma yuborildi</h2></div>")

    return page("To‘lov","""<div class="box">
    <form method="post">
    <input placeholder="Karta (TEST)">
    <input placeholder="CVV">
    <button class="btn">To‘lash</button>
    </form></div>""")

@app.route("/contact", methods=["GET","POST"])
def contact():
    msg=""
    if request.method=="POST":
        name=request.form["name"]
        phone=request.form["phone"]
        email=request.form["email"]
        text=request.form["text"]

        if len(name)<3 or "@" not in email or not phone.startswith("+998"):
            msg="<p style='color:red'>Ma'lumotlar noto‘g‘ri</p>"
        else:
            send_to_telegram(f"📩 XABAR\n{name}\n{phone}\n{text}")
            msg="<p style='color:lightgreen'>Xabar yuborildi</p>"

    return page("Aloqa",f"""
    <div class="box">
    {msg}
    <form method="post">
    <input name="name" placeholder="Ism">
    <input name="phone" placeholder="+998...">
    <input name="email" placeholder="Email">
    <textarea name="text" placeholder="Xabar"></textarea>
    <button class="btn">Yuborish</button>
    </form></div>""")

@app.route("/admin", methods=["GET","POST"])
def admin():
    if request.method=="POST":
        if request.form.get("password") != ADMIN_PASSWORD:
            return page("Xato","❌ Parol xato")
        menu[request.form["name"]] = {
            "price": int(request.form["price"]),
            "img": request.form["img"]
        }
        return redirect("/")

    order_html = "".join(
        f"<p>{', '.join(o['items'])} — {o['total']} so'm</p>"
        for o in orders
    ) or "<p>Buyurtma yo‘q</p>"

    return page("Admin",f"""
    <div class="box">
    <h3>Buyurtmalar</h3>
    {order_html}
    </div>""")

if __name__ == "__main__":
    app.run()