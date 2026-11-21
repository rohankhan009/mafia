# 📱 Telegram Bulk SMS Dispatcher Bot

Bulk SMS distribution system built with Python, Telegram Bot API, and Firebase Realtime Database.

---

## 🆕 Version 3 — naya bottom menu

- ⌨️ **Persistent bottom menu** — chat ke niche hamesha bade tap-friendly buttons
  (Send Bulk SMS, Upload Data File, Message Templates, Manage Firebase, Devices,
  Status, History, Settings, Daily Usage, Help). `/start` dabate hi aa jaate hain.
- 📅 **Daily Usage** screen — aaj kitne SMS bheje/fail hue, campaign-wise.
- 📤 **Behtar live progress** — Sent / Failed / Pending, `msg/s` speed, Phones count
  aur ETA (reference UI jaisa).

---

## 🆕 Version 2 — naye features

- 🚦 **Rate-Limit Control** — Settings mein global SMS/min cap (Off / 30 / 60 / 120 / 300).
- 📋 **CSV Delivery Logs** — har campaign ke end par poori delivery CSV apne-aap chat mein aa jaati hai (number, status, device, time, error).
- ⏰ **Auto-Schedule** — campaign ko baad ke time par chalao (`+30`, `14:30`, ya `2026-01-20 09:00`).
- 📊 **Live Dashboard Refresh** — dashboard har 6 sec auto-update (▶️/⏹ toggle).
- 📋 **Bulk Firebase Add** — ek saath kai Firebase URLs paste karke add karo.

> Note: Scheduled campaigns bot ke chalte rehne par hi fire hote hain. Agar bot restart hota hai to pending schedules dobara set karne padenge (standalone script limitation).

---

## 🆕 What's fixed & faster (earlier update)

- ⚡ **Firebase scan 2x+ faster** — har database ab ek hi baar fetch hota hai
  (pehle poora `/clients` tree do baar download hota tha), connection pooling +
  retries ke saath, aur multiple Firebases ab **parallel** scan hote hain.
- 🚀 **SMS sending ab truly parallel** — saare device workers background threads
  par chalte hain (blocking requests event-loop ko rok nahi rahe), aur DB writes
  ab batch mein hote hain → 100k numbers smoothly.
- 🔁 **Resend Failed** button — sirf fail hue numbers dobara bhejo.
- 📥 **Export Numbers** button — campaign ke numbers `.txt` mein download karo.
- 🐛 **Bug fixes** — main menu ke counts ab sahi dikhte hain; campaign SIM slot
  ab sahi (SIM 1 = slot 0, SIM 2 = slot 1).
- 🖥️ VPS sizing + setup guide: dekho **VPS_GUIDE.md**.

**TL;DR VPS:** 100k/din ke liye **2 vCPU / 4 GB RAM / 50–80 GB SSD** kaafi hai
(bottleneck gateway hota hai, CPU nahi). Details VPS_GUIDE.md mein.


---

## ⚡ How It Works

```
[ Telegram User ]
       │
       ▼ (Sends SMS text + Numbers list)
[ Telegram Bot (bot.py) ]
       │
       ▼ (Distributes targets evenly across online devices)
[ Firebase RTDB: PUT /clients/{deviceId}/sendSms.json ]
       │
       ▼ (Realtime event listener in Android App)
[ Android Phones (SmsManager) ] ──> Sends SMS to Targets!
```

---

## 🚀 Quick Setup

1. **Get a Telegram Bot Token**:
   - Open Telegram, search for `@BotFather`.
   - Send `/newbot` and follow instructions.
   - Copy the HTTP API token.

2. **Configure [config.py](file:///C:/Users/MANSI/.gemini/antigravity-ide/scratch/sms-bot/config.py)**:
   - Paste your token into `BOT_TOKEN`:
     ```python
     BOT_TOKEN = "1234567890:ABCdefGHIjklMNOpqrSTUvwxYZ"
     ```
   - Your Firebase Realtime DB URL is already pre-configured:
     ```python
     DEFAULT_FIREBASE_URL = "https://berlinxmirrorfinalboss-default-rtdb.firebaseio.com"
     ```

3. **Start the Bot**:
   - Double-click [`start.bat`](file:///C:/Users/MANSI/.gemini/antigravity-ide/scratch/sms-bot/start.bat) or run:
     ```bash
     python bot.py
     ```

---

## 🕹️ Bot Commands & Features

| Command | Action |
|---|---|
| `/start` | Open main dashboard with interactive buttons |
| `/send` | Launch step-by-step Bulk SMS Campaign wizard |
| `/devices` | View all online Android devices, battery, and SIM carrier details |
| `/seturl` | Change Firebase Realtime Database URL dynamically |
| `/cancel` | Cancel current wizard / action |

---

## 📋 Campaign Wizard Flow

1. **Online Worker Verification**:
   - Bot automatically checks Firebase RTDB.
   - Detects all devices with `status: true` (e.g. TECNO, Vivo, Moto, Oppo).
2. **SMS Template**:
   - Send your exact SMS text.
   - Shows character counter and estimated SMS parts (160 chars/part).
3. **Numbers List**:
   - Send numbers directly in chat or upload a `.txt` file.
   - Automatically cleans whitespace, dashes, duplicates, and normalizes Indian format (+91).
4. **Distribution & Settings**:
   - Select SIM Slot 0 (SIM 1) or Slot 1 (SIM 2).
   - Select throttle delay (1s, 2s, 5s) to avoid carrier blocks.
   - Evenly balances numbers across all available online phones.
5. **Live Blast Progress**:
   - Realtime visual progress bar: `[████████░░░░] 60%`
   - Dispatched count, failed count, remaining targets.
   - `🛑 STOP CAMPAIGN` button to pause/abort anytime.
