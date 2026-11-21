# 🖥️ VPS Setup & Sizing Guide — Bulk SMS Telegram Bot

Ye guide Hinglish mein hai. Aapka target: **~1 lakh (100k) SMS/din** + Firebase scan.

---

## 1) Kitna bada VPS lu? (Sizing)

**Short answer:** Ek chhota VPS kaafi hai. Asli bottleneck aapka SMS gateway
(Android phones + carrier) hota hai — CPU/RAM nahi. Ye bot ab blocking I/O ko
background threads par chalata hai, to ek single core bhi kai devices ko
parallel handle kar leta hai.

| Load (per din)        | Recommended VPS            | Note |
|-----------------------|----------------------------|------|
| 20k–50k SMS           | 1 vCPU / 2 GB RAM / 30 GB SSD | Starter ke liye theek |
| **~100k SMS (target)**| **2 vCPU / 4 GB RAM / 50–80 GB SSD** | ✅ Recommended |
| 100k+ with heavy parallel sending / many Firebases | 4 vCPU / 8 GB RAM / 80 GB SSD | Extra headroom |

**Kyun 2 vCPU / 4 GB kaafi hai:**
- Bot sirf commands Firebase par likhta hai; actual SMS aapke Android phones bhejte hain.
- Throughput = (online devices) × (per-device speed). Ye phone/carrier par depend karta hai, VPS par nahi.
- SQLite + batched writes 100k rows easily sambhal lete hain.

👉 **Provider:** DigitalOcean, Hetzner, Vultr, Contabo — koi bhi Ubuntu 22.04/24.04 VPS chalega.
Location aise chuno jo Firebase (Google) ke paas ho taaki scan aur bhi tez ho.

---

## 2) VPS par install (Ubuntu)

```bash
# 1. System update
sudo apt update && sudo apt install -y python3 python3-pip python3-venv

# 2. Project upload karo (scp/git) aur andar jao
cd /path/to/smssendbulk

# 3. Virtual env + dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 4. config.py mein apna BOT_TOKEN aur ADMIN_IDS daalo

# 5. Test run
python3 bot.py
```

Bot chalu hone par Telegram par `/start` bhejo.

---

## 3) 24×7 chalane ke liye (systemd service)

`/etc/systemd/system/smsbot.service` banao:

```ini
[Unit]
Description=Bulk SMS Telegram Bot
After=network.target

[Service]
WorkingDirectory=/path/to/smssendbulk
ExecStart=/path/to/smssendbulk/venv/bin/python3 bot.py
Restart=always
RestartSec=5
User=root

[Install]
WantedBy=multi-user.target
```

Phir:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now smsbot
sudo systemctl status smsbot      # chal raha hai check karo
journalctl -u smsbot -f           # live logs
```

Ab server reboot ho ya crash ho, bot apne aap wapas chalu ho jayega.

---

## 4) Speed tips (100k ke liye)

- **Zyada online devices = zyada speed.** 1 phone ~1 SMS / delay-second deta hai.
  10 online phones + 1s delay ≈ 10 SMS/sec ≈ 36k/ghanta.
- Campaign settings mein **Delay** ko 1s par rakho agar carrier block na kare.
- Bade lists ko pehle **Data Files** mein save karke rakho (fast reuse).
- Firebase scan ab single-pass + parallel hai; agar fir bhi slow lage to aapka
  Firebase region door ho sakta hai — VPS ko Firebase ke paas (US/Europe) rakho.
