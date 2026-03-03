from flask import Flask, render_template_string, request, session, redirect, url_for
from datetime import timedelta
import os
import random
import uuid

app = Flask(__name__)

app.secret_key = os.environ.get('FLASK_SECRET_KEY') or "TEMPORARY_KEY_GANTI_SEKARANG"
app.permanent_session_lifetime = timedelta(minutes=60)

# Harga fixed per akun
harga_silver = 35000
harga_gold = 35000

nomor_dana = "081266617068"
dana_username = "Noni"
gambar_qris = "/static/qris.jpg"
nomor_wa = "6281373318253"

@app.route("/", methods=["GET", "POST"])
def home():
    error = None
    if request.method == "POST":
        if request.form.get("honeypot"):
            return "Spam detected! ❌"

        user_captcha = request.form.get("captcha")
        correct_answer = session.get("captcha_answer")
        if not user_captcha or int(user_captcha) != correct_answer:
            error = "CAPTCHA SALAH! Coba lagi."
        else:
            akun_type = request.form.get("akun_type")
            wa_pembeli = request.form.get("wa_pembeli")

            if not akun_type or not wa_pembeli:
                error = "Lengkapi semua data (pilih akun + nomor WA)!"
            else:
                if akun_type == "silver":
                    total = harga_silver
                elif akun_type == "gold":
                    total = harga_gold
                else:
                    error = "Pilihan akun tidak valid!"
                    return render_template_string(home_template(), error=error, harga_silver=harga_silver, harga_gold=harga_gold)

                session['akun_type'] = akun_type
                session['total'] = total
                session['wa_pembeli'] = wa_pembeli
                session['order_id'] = str(uuid.uuid4())[:8].upper()
                return redirect(url_for('pembayaran'))

    num1 = random.randint(3, 12)
    num2 = random.randint(3, 12)
    session["captcha_answer"] = num1 + num2
    captcha_question = f"{num1} + {num2} = ?"

    return render_template_string("""
    <html>
    <head>
        <title>CERFOR STORE - Pilih Akun</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body{background:#0f0f0f;color:white;font-family:Arial;padding:20px;}
            .box{background:#1a1a1a;padding:25px;border-radius:20px;box-shadow:0 0 25px cyan;max-width:500px;margin:auto;}
            h1{text-align:center;color:cyan;}
            button{width:100%;padding:15px;border:none;border-radius:12px;font-weight:bold;cursor:pointer;margin-top:15px;}
            .price{font-size:20px;color:lime;margin-top:10px;}
            .total{font-size:24px;color:yellow;margin-top:15px;}
            input[type="text"], input[type="tel"]{padding:10px;width:100%;margin-top:5px;border-radius:8px;border:none;background:#222;color:white;}
            .hidden{display:none;}
            img.akun{width:100%;border-radius:12px;margin:15px 0;box-shadow:0 0 15px cyan;}
            .akun-option{margin-bottom:30px;text-align:center;}
            .error{color:red; text-align:center; margin:10px 0;}
            .rgb-btn {
                background: linear-gradient(45deg, #ff0000, #ff7f00, #ffff00, #00ff00, #0000ff, #8b00ff, #ff00ff);
                background-size: 400% 400%;
                animation: rgbGradient 8s ease infinite;
                color: white;
                box-shadow: 0 0 20px rgba(255,255,255,0.5);
                transition: all 0.3s;
            }
            .rgb-btn:hover {
                box-shadow: 0 0 30px rgba(255,255,255,0.8);
                transform: scale(1.05);
            }
            @keyframes rgbGradient {
                0% {background-position: 0% 50%;}
                50% {background-position: 100% 50%;}
                100% {background-position: 0% 50%;}
            }
        </style>
    </head>
    <body>
    <div class="box">
        <h1>CERFOR STORE</h1>
        <h2 style="text-align:center;color:lime;">Pilih Akun yang Mau Dibeli</h2>

        {% if error %}
            <p class="error">{{ error }}</p>
        {% endif %}

        <form method="post" id="form">
            <div class="akun-option">
                <h3>Akun Silver</h3>
                <img class="akun" src="/static/akun_silver.jpg" alt="Akun Silver">
                <p style="color:#ffeb3b;">Full upgrade, mobil keren, level tinggi</p>
                <p class="price">Harga: Rp {{ harga_silver }}</p>
                <button type="submit" name="akun_type" value="silver" class="rgb-btn">Pilih Akun Silver</button>
            </div>

            <div class="akun-option">
                <h3>Akun Gold</h3>
                <img class="akun" src="/static/akun_gold.jpg" alt="Akun Gold">
                <p style="color:#ffeb3b;">VIP premium, semua fitur unlocked, uang banyak</p>
                <p class="price">Harga: Rp {{ harga_gold }}</p>
                <button type="submit" name="akun_type" value="gold" class="rgb-btn">Pilih Akun Gold</button>
            </div>

            <h3 style="margin-top:30px;">Nomor WA Pembeli (wajib):</h3>
            <input type="tel" name="wa_pembeli" placeholder="08xxxxxxxxxx" required autocomplete="off">

            <h3 style="margin-top:20px;">Verifikasi CAPTCHA:</h3>
            <p style="margin:8px 0;">{{ captcha_question }}</p>
            <input type="text" name="captcha" placeholder="Jawaban" required autocomplete="off">

            <input type="text" name="honeypot" class="hidden" autocomplete="off">
        </form>

        <button class="testi-btn" onclick="mintaTestimoni()">Minta Testimoni ke WA</button>
    </div>

    <script>
    function mintaTestimoni() {
        let pesan = "Halo, saya ingin minta testimoni atau review setelah beli akun. Terima kasih!";
        window.location.href = "https://wa.me/6281373318253?text=" + encodeURIComponent(pesan);
    }
    </script>
    </body>
    </html>
    """, harga_silver=harga_silver, harga_gold=harga_gold, captcha_question=captcha_question)

@app.route("/pembayaran")
def pembayaran():
    akun_type = session.get('akun_type')
    total = session.get('total')
    order_id = session.get('order_id')
    wa_pembeli = session.get('wa_pembeli')

    if not akun_type or not total or not order_id or not wa_pembeli:
        return redirect(url_for('home'))

    return render_template_string("""
    <html>
    <head>
        <title>Pembayaran - CERFOR STORE</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body{background:#0f0f0f;color:white;font-family:Arial;padding:20px;}
            .box{background:#1a1a1a;padding:25px;border-radius:20px;box-shadow:0 0 25px cyan;max-width:500px;margin:auto;}
            h1{text-align:center;color:cyan;}
            h2{color:#00ffff;}
            h3{color:lime;}
            img{width:100%;margin:15px 0;border-radius:12px;}
            button, .toggle-btn{width:100%;padding:15px;border:none;border-radius:12px;font-weight:bold;cursor:pointer;margin-top:10px;}
            .rgb-btn {
                background: linear-gradient(45deg, #ff0000, #ff7f00, #ffff00, #00ff00, #0000ff, #8b00ff, #ff00ff);
                background-size: 400% 400%;
                animation: rgbGradient 8s ease infinite;
                color: white;
                box-shadow: 0 0 20px rgba(255,255,255,0.5);
                transition: all 0.3s;
            }
            .rgb-btn:hover {
                box-shadow: 0 0 30px rgba(255,255,255,0.8);
                transform: scale(1.05);
            }
            @keyframes rgbGradient {
                0% {background-position: 0% 50%;}
                50% {background-position: 100% 50%;}
                100% {background-position: 0% 50%;}
            }
            .payment-tabs {display:flex; justify-content:space-around; margin:20px 0;}
            .tab-btn {padding:12px;background:#333;color:white;border:none;border-radius:8px;cursor:pointer;flex:1;margin:0 5px;transition:all 0.3s;}
            .tab-btn.active, .tab-btn:hover {background:linear-gradient(45deg, #ff0000, #ffff00, #00ff00); color:black; box-shadow:0 0 15px #ffff00;}
            .payment-content {display:none; margin-top:15px;}
            .payment-content.active {display:block;}
            .total{font-size:24px;color:yellow;margin-top:15px;}
            .back-btn{background:#444;color:white;}
            .order-id{font-size:18px;color:lime;margin:10px 0;}
            .instruksi {color:#ffeb3b; font-size:16px; margin-top:15px; text-align:center;}
            .dana-info, .qris-info {display:none; margin-top:10px; padding:10px; background:#222; border-radius:8px;}
            .toggle-btn {background:#00ff9d; color:black;}
        </style>
    </head>
    <body>
    <div class="box">
        <h1>PEMBAYARAN</h1>
        <p class="order-id"><strong>Order ID:</strong> {{ order_id }}</p>
        <p><strong>WA Pembeli:</strong> {{ wa_pembeli }}</p>
        
        <h3>Detail Pembelian:</h3>
        <p>Akun: {{ akun_type.capitalize() }}</p>
        <div class="total">Total: Rp {{ total }}</div>

        <h2>Pilih Metode Bayar:</h2>
        <div class="payment-tabs">
            <button class="tab-btn active" onclick="showTab('dana')">DANA</button>
            <button class="tab-btn" onclick="showTab('qris')">All Payment / QRIS</button>
        </div>

        <div id="dana" class="payment-content active">
            <h3>DANA</h3>
            <button class="toggle-btn" onclick="toggleDana('dana-info')">Tampilkan Nomor DANA</button>
            <div id="dana-info" class="dana-info">
                <p>Nomor: <strong>{{ nomor_dana }}</strong></p>
                <p>Nama: <strong>{{ dana_username }}</strong></p>
            </div>
        </div>

        <div id="qris" class="payment-content">
            <h3>All Payment / QRIS</h3>
            <p style="color:#ffeb3b; font-weight:bold;">Scan QRIS dengan aplikasi payment kamu</p>
            <button class="toggle-btn" onclick="toggleDana('qris-info')">Tampilkan QRIS</button>
            <div id="qris-info" class="qris-info">
                <p>Screenshot QRIS di bawah ini</p>
                <img src="{{ gambar_qris }}" alt="QRIS Pembayaran">
                <a href="/static/qris.jpg" download="QRIS-CERFOR-STORE.jpg" class="rgb-btn download-btn">📥 Download Gambar QRIS</a>
            </div>
        </div>

        <p style="margin-top:20px;">Setelah transfer, klik tombol di bawah untuk konfirmasi via WhatsApp. Kirim foto bukti + Order ID!</p>

        <button onclick="konfirmasiWA()" class="rgb-btn">SUDAH BAYAR (Konfirmasi WA)</button>

        <p class="instruksi">Kirim foto bukti TF + Order ID ke WA ini. Admin akan cek & kirim akun dalam 1 menit. Tergantung Admin online/offline nya</p>

        <a href="{{ url_for('home') }}"><button class="back-btn">KEMBALI KE PILIHAN</button></a>
    </div>

    <script>
    function showTab(tabName) {
        document.querySelectorAll('.payment-content').forEach(el => el.classList.remove('active'));
        document.getElementById(tabName).classList.add('active');
        document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));
        event.target.classList.add('active');
    }

    function toggleDana(infoId) {
        var info = document.getElementById(infoId);
        if (info.style.display === "none" || info.style.display === "") {
            info.style.display = "block";
        } else {
            info.style.display = "none";
        }
    }

    function konfirmasiWA() {
        let pesan = "Order ID: {{ order_id }}\\nWA Pembeli: {{ wa_pembeli }}\\nAkun: {{ akun_type }}\\nTotal: Rp {{ total }}\\n\\nSaya sudah bayar. Ini bukti transfer (attach foto ya).";
        window.location.href = "https://wa.me/{{ nomor_wa }}?text=" + encodeURIComponent(pesan);
    }
    </script>
    </body>
    </html>
    """, akun_type=akun_type, total=total, order_id=order_id, wa_pembeli=wa_pembeli,
       nomor_dana=nomor_dana, dana_username=dana_username,
       gambar_qris=gambar_qris, nomor_wa=nomor_wa)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
