from flask import Flask, render_template_string, request, session, redirect, url_for
from datetime import timedelta
import os
import random
import uuid

app = Flask(__name__)

app.secret_key = os.environ.get('FLASK_SECRET_KEY') or "TEMPORARY_KEY_GANTI_SEKARANG"
app.permanent_session_lifetime = timedelta(minutes=60)

harga_akun = 35000

garansi_list = [
    {"name": "NO GARANSI", "price": 0},
    {"name": "30 HARI", "price": 25000},
    {"name": "60 HARI", "price": 45000},
    {"name": "120 HARI", "price": 85000},
    {"name": "360 HARI", "price": 175000},
    {"name": "UNLIMITED", "price": 300000},
]

nomor_dana = "081266617068"
dana_username = "Noni"
gambar_qris = "/static/qris.jpg"
nomor_wa = "6281373318253"

def get_garansi_price(name):
    for g in garansi_list:
        if g["name"] == name:
            return g["price"]
    return None

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
            garansi = request.form.get("garansi")
            harga_garansi_str = request.form.get("harga_garansi")
            wa_pembeli = request.form.get("wa_pembeli")

            if not garansi or not harga_garansi_str or not wa_pembeli:
                error = "Lengkapi semua data (garansi + nomor WA)!"
            else:
                try:
                    harga_garansi = int(harga_garansi_str)
                    if harga_garansi != get_garansi_price(garansi):
                        error = "Harga garansi tidak valid!"
                    else:
                        total = harga_akun + harga_garansi
                        session['garansi'] = garansi
                        session['total'] = total
                        session['wa_pembeli'] = wa_pembeli
                        session['order_id'] = str(uuid.uuid4())[:8].upper()
                        return redirect(url_for('pembayaran'))
                except:
                    error = "Terjadi kesalahan, coba lagi."

    num1 = random.randint(3, 12)
    num2 = random.randint(3, 12)
    session["captcha_answer"] = num1 + num2
    captcha_question = f"{num1} + {num2} = ?"

    return render_template_string("""
    <html>
    <head>
        <title>CERFOR STORE</title>
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
            img.product{width:100%;border-radius:12px;margin:15px 0;box-shadow:0 0 15px cyan;}
            .testi-btn{background:#4CAF50;color:white;margin-top:30px;padding:15px;border-radius:12px;font-weight:bold;cursor:pointer;width:100%;border:none;}
            .error{color:red; text-align:center; margin:10px 0;}
            .payment-tabs {display:flex; justify-content:space-around; margin:20px 0;}
            .tab-btn {padding:12px;background:#333;color:white;border:none;border-radius:8px;cursor:pointer;flex:1;margin:0 5px;transition:all 0.3s;}
            .tab-btn.active, .tab-btn:hover {background:linear-gradient(45deg, #ff0000, #ffff00, #00ff00); color:black; box-shadow:0 0 15px #ffff00;}
            .payment-content {display:none; margin-top:15px;}
            .payment-content.active {display:block;}
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
            .instruksi {color:#ffeb3b; font-size:16px; margin-top:15px; text-align:center;}
        </style>
    </head>
    <body>
    <div class="box">
        <h1>CERFOR STORE</h1>
        
        <h3 style="text-align:center; color:lime; margin-bottom:10px;">(DESKRIPSI AKUN CARXSTREET👇👇)</h3>
        <img class="product" src="/static/akun_premium.jpg" alt="Akun CarX Street Premium">

        <div class="price">Harga Akun: Rp 35.000</div>

        {% if error %}
            <p class="error">{{ error }}</p>
        {% endif %}

        <form method="post" id="form">
            <h3>🕑PAKET GARANSI || 👇👇</h3>
            {% for g in garansi_list %}
                <input type="radio" name="garansi" value="{{g.name}}" 
                       data-price="{{g.price}}" required>
                {{g.name}} || HARGA=TAMBAH {{g.price//1000}}K💵<br>
            {% endfor %}

            <input type="hidden" name="harga_garansi" id="harga_garansi">

            <h3 style="margin-top:20px;">Nomor WA Pembeli (wajib):</h3>
            <input type="tel" name="wa_pembeli" placeholder="08xxxxxxxxxx" required autocomplete="off">

            <h3 style="margin-top:20px;">Verifikasi CAPTCHA:</h3>
            <p style="margin:8px 0;">{{ captcha_question }}</p>
            <input type="text" name="captcha" placeholder="Jawaban" required autocomplete="off">

            <input type="text" name="honeypot" class="hidden" autocomplete="off">

            <div class="total">
                Total: Rp <span id="total">{{ harga_akun }}</span>
            </div>

            <button type="submit" class="rgb-btn">LANJUT KE PEMBAYARAN</button>
        </form>

        <button class="testi-btn" onclick="mintaTestimoni()">Minta Testimoni ke WA</button>
    </div>

    <script>
    const hargaAkun = {{ harga_akun }};
    const radios = document.querySelectorAll("input[name='garansi']");
    const totalText = document.getElementById("total");
    const hiddenHarga = document.getElementById("harga_garansi");

    function updateTotal(){
        let selected = document.querySelector("input[name='garansi']:checked");
        if (selected) {
            let hargaGaransi = parseInt(selected.getAttribute("data-price"));
            let total = hargaAkun + hargaGaransi;
            totalText.innerText = total;
            hiddenHarga.value = hargaGaransi;
        } else {
            totalText.innerText = hargaAkun;
            hiddenHarga.value = 0;
        }
    }

    radios.forEach(r => r.addEventListener("change", updateTotal));
    updateTotal();

    function mintaTestimoni() {
        let pesan = "Halo, saya ingin minta testimoni atau review setelah beli akun. Terima kasih!";
        window.location.href = "https://wa.me/6281373318253?text=" + encodeURIComponent(pesan);
    }
    </script>
    </body>
    </html>
    """, garansi_list=garansi_list, harga_akun=harga_akun, captcha_question=captcha_question)

@app.route("/pembayaran")
def pembayaran():
    garansi = session.get('garansi')
    total = session.get('total')
    order_id = session.get('order_id')
    wa_pembeli = session.get('wa_pembeli')

    if not garansi or not total or not order_id or not wa_pembeli:
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
            button{width:100%;padding:15px;border:none;border-radius:12px;font-weight:bold;cursor:pointer;margin-top:10px;}
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
            .download-btn{background:#00ff9d;color:black;margin-top:10px;}
        </style>
    </head>
    <body>
    <div class="box">
        <h1>PEMBAYARAN</h1>
        <p class="order-id"><strong>Order ID:</strong> {{ order_id }}</p>
        <p><strong>WA Pembeli:</strong> {{ wa_pembeli }}</p>
        
        <h3>Detail Pembelian:</h3>
        <p>Garansi: {{ garansi }}</p>
        <div class="total">Total: Rp {{ total }}</div>

        <h2>Pilih Metode Bayar:</h2>
        <div class="payment-tabs">
            <button class="tab-btn active" onclick="showTab('dana')">DANA</button>
            <button class="tab-btn" onclick="showTab('qris')">All Payment / QRIS</button>
        </div>

        <div id="dana" class="payment-content active">
            <h3>DANA</h3>
            <p>Nomor: <strong>{{ nomor_dana }}</strong><br>
               Nama: <strong>{{ dana_username }}</strong></p>
        </div>

        <div id="qris" class="payment-content">
            <h3>All Payment / QRIS</h3>
            <p style="color:#ffeb3b; font-weight:bold;">Screenshot QRIS di bawah ini</p>
            <p>Scan dengan aplikasi payment kamu (DANA, GoPay, OVO, ShopeePay, dll)</p>
            <img src="{{ gambar_qris }}" alt="QRIS Pembayaran">
            <a href="/static/qris.jpg" download="QRIS-CERFOR-STORE.jpg" class="rgb-btn download-btn">📥 Download Gambar QRIS</a>
        </div>

        <p style="margin-top:20px;">Setelah transfer, klik tombol di bawah untuk konfirmasi via WhatsApp. Kirim foto bukti + Order ID!</p>

        <button onclick="konfirmasiWA()" class="rgb-btn">SUDAH BAYAR (Konfirmasi WA)</button>

        <p class="instruksi">Kirim foto bukti TF + Order ID ke WA ini. Admin akan cek & kirim akun dalam 5-15 menit.</p>

        <a href="{{ url_for('home') }}"><button class="back-btn">KEMBALI KE PILIHAN</button></a>
    </div>

    <script>
    function showTab(tabName) {
        document.querySelectorAll('.payment-content').forEach(el => el.classList.remove('active'));
        document.getElementById(tabName).classList.add('active');
        document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));
        event.target.classList.add('active');
    }

    function konfirmasiWA() {
        let pesan = "Order ID: {{ order_id }}\\nWA Pembeli: {{ wa_pembeli }}\\nGaransi: {{ garansi }}\\nTotal: Rp {{ total }}\\n\\nSaya sudah bayar. Ini bukti transfer (attach foto ya).";
        window.location.href = "https://wa.me/{{ nomor_wa }}?text=" + encodeURIComponent(pesan);
    }
    </script>
    </body>
    </html>
    """, garansi=garansi, total=total, order_id=order_id, wa_pembeli=wa_pembeli,
       nomor_dana=nomor_dana, dana_username=dana_username,
       gambar_qris=gambar_qris, nomor_wa=nomor_wa)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
