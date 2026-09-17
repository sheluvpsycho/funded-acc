# 🚀 FundedNext Python Bot - Setup Guide

## **WHY PYTHON BOT?** ✅

✅ Runs on **ANY computer** (Windows, Mac, Linux, Chromebook)  
✅ No NinjaTrader needed  
✅ Can run on **free cloud server**  
✅ Easy to modify and customize  
✅ Works 24/7 if hosted on VPS  

---

## **OPTION 1: RUN ON YOUR COMPUTER** 💻

### **Step 1: Install Python**

**Windows/Mac/Linux:**
- Go to https://www.python.org/downloads/
- Download Python 3.9 or newer
- Install it

**Chromebook:**
- Can't run Python directly
- Skip to Option 2 (Cloud VPS)

### **Step 2: Install Required Libraries**

Open Terminal/Command Prompt and run:

```bash
pip install requests
```

### **Step 3: Get Your API Key**

1. Log into FundedNext account
2. Go to: **Settings → API Keys**
3. Create new API key
4. Copy the key

### **Step 4: Set Environment Variable**

**Windows (Command Prompt):**
```bash
set FUNDEDNEXT_API_KEY=your_api_key_here
```

**Mac/Linux/Chromebook (Terminal):**
```bash
export FUNDEDNEXT_API_KEY=your_api_key_here
```

### **Step 5: Run the Bot**

```bash
python fundednext_bot.py
```

**You should see:**
```
=======================================
FundedNext Challenge Bot Initialized
Account Size: $50,000.00
Daily Profit Target: $2,500.00
Max Daily Loss: $1,500.00
Risk Per Trade: $200.00
=======================================
```

✅ **BOT IS RUNNING!**

---

## **OPTION 2: RUN ON CLOUD VPS** ☁️

### **Why Cloud VPS?**
- Runs 24/7 without your computer
- Works from Chromebook
- Professional setup
- Cost: $5-15/month

### **Step 1: Rent a VPS**

**Best providers:**

| Provider | Price | Setup |
|----------|-------|-------|
| **DigitalOcean** | $5/month | Easy |
| **Linode** | $10/month | Easy |
| **AWS** | $15/month | Medium |
| **Vultr** | $5/month | Easy |

**Recommended: DigitalOcean** (easiest for beginners)

### **Step 2: Create VPS**

1. Go to DigitalOcean.com
2. Click **Create → Droplets**
3. Select:
   - OS: **Ubuntu 22.04**
   - Size: **Basic ($5/month)**
   - Region: **Closest to you**
4. Click **Create Droplet**
5. Wait 2-3 minutes for setup
6. You get IP address

### **Step 3: Connect to VPS**

**On Mac/Linux (Terminal):**
```bash
ssh root@YOUR_IP_ADDRESS
```

**On Windows (PowerShell):**
```bash
ssh root@YOUR_IP_ADDRESS
```

**On Chromebook:**
- Use **Secure Shell App** (from Chrome Web Store)
- Connect to YOUR_IP_ADDRESS

### **Step 4: Install Python & Bot**

Copy-paste these commands:

```bash
# Update system
apt update && apt upgrade -y

# Install Python & pip
apt install python3 python3-pip -y

# Install required packages
pip3 install requests

# Create bot directory
mkdir /root/fundednext-bot
cd /root/fundednext-bot

# Create bot file
nano fundednext_bot.py
```

Then:
1. Paste the entire `fundednext_bot.py` code
2. Press **Ctrl+X** → **Y** → **Enter**

### **Step 5: Set API Key**

```bash
export FUNDEDNEXT_API_KEY=your_api_key_here
```

### **Step 6: Run Bot**

```bash
python3 fundednext_bot.py
```

### **Step 7: Keep Bot Running 24/7**

Use `screen` or `nohup`:

**Option A (Screen - Recommended):**
```bash
screen -S tradingbot
python3 fundednext_bot.py

# Press Ctrl+A then D to detach (bot keeps running)
# Later, reconnect with: screen -r tradingbot
```

**Option B (Nohup):**
```bash
nohup python3 fundednext_bot.py > tradingbot.log 2>&1 &
```

---

## **BOT CONFIGURATION**

### **Default Settings:**
```python
account_size = 50000          # $50K
daily_profit_target = 2500    # $2,500
max_daily_loss = 1500         # $1,500
risk_per_trade = 200          # $200 per trade
```

### **Modify Settings:**

Edit `fundednext_bot.py` and find:

```python
bot = FundedNextBot(
    api_key=api_key,
    account_size=50000,           # ← CHANGE HERE
    daily_profit_target=2500,     # ← CHANGE HERE
    max_daily_loss=1500,          # ← CHANGE HERE
    risk_per_trade=200            # ← CHANGE HERE
)
```

### **Trading Parameters:**

```python
# Entry signals
fast_ma_period = 9             # Fast moving average
slow_ma_period = 21            # Slow moving average
breakout_threshold = 0.0015    # 0.15% breakout

# Exit rules
take_profit_points = 20        # 20 ticks profit
stop_loss_points = 15          # 15 ticks loss
```

---

## **HOW THE BOT WORKS**

### **Trading Hours:**
- **Start:** 9:30 AM EST
- **End:** 4:00 PM EST
- **No new entries:** After 3:30 PM
- **Auto-close:** 4:00 PM

### **Entry Signals:**

**LONG Entry:**
- Fast MA > Slow MA (by 0.15%)
- Price > Fast MA
- Opens position

**SHORT Entry:**
- Fast MA < Slow MA (by 0.15%)
- Price < Fast MA
- Opens position

### **Exit Signals:**

**Take Profit:**
- Long: Price +20 ticks above entry
- Short: Price -20 ticks below entry

**Stop Loss:**
- Long: Price -15 ticks below entry
- Short: Price +15 ticks above entry

**Daily Stop:**
- Profit reaches $2,500 → Stop all trading ✅
- Loss reaches $1,500 → Stop all trading ✗

---

## **MONITORING THE BOT**

### **Check Bot Status:**

**On Local Computer:**
- Just look at terminal window
- See real-time trades & P&L

**On Cloud VPS:**
```bash
# Attach to running bot
screen -r tradingbot

# Or check log file
tail -f tradingbot.log
```

### **What You'll See:**

```
2026-09-16 10:15:33 - INFO - Trading Cycle: 2026-09-16 10:15:33
2026-09-16 10:15:33 - INFO - Symbol: MNQ | Price: 16850.50
2026-09-16 10:15:33 - INFO - Fast MA(9): 16845.20 | Slow MA(21): 16820.10
2026-09-16 10:15:33 - INFO - Daily P&L: $0.00
2026-09-16 10:15:33 - INFO - Progress: $0.00 / $2,500.00

2026-09-16 10:16:05 - INFO - ORDER PLACED: BUY 7 MNQ @ 16850.75
2026-09-16 10:16:05 - INFO - Order ID: order_abc123xyz

2026-09-16 10:22:15 - INFO - POSITION CLOSED: order_abc123xyz - Reason: TAKE_PROFIT
2026-09-16 10:22:15 - INFO - Daily P&L: $245.00
```

---

## **TROUBLESHOOTING**

### **Bot won't start:**
```
Error: FUNDEDNEXT_API_KEY not set

Fix: Set the environment variable
Windows: set FUNDEDNEXT_API_KEY=your_key
Mac/Linux: export FUNDEDNEXT_API_KEY=your_key
```

### **Connection errors:**
```
Error: Error fetching market data

Fix: Check internet connection
Fix: Verify API key is correct
Fix: Check if FundedNext API is online
```

### **Orders not executing:**
```
Fix 1: Verify API key has trading permissions
Fix 2: Check account has sufficient balance ($50K)
Fix 3: Confirm trading hours (9:30 AM - 4:00 PM EST)
Fix 4: Check if symbol MNQ is tradeable
```

### **Bot losing too much:**
```
Reduce risk: Change risk_per_trade from 200 to 100
Tighter stops: Change stop_loss_points from 15 to 10
Higher targets: Change take_profit_points from 20 to 25
```

---

## **DAILY CHECKLIST**

### **Morning (Before 9:30 AM):**
```
☐ Bot is running
☐ No error messages
☐ API key is set
☐ Account balance shows $50K
☐ Symbol MNQ is tradeable
```

### **During Trading (9:30 AM - 4:00 PM):**
```
☐ Monitor bot every 30-60 mins
☐ Watch P&L progress
☐ Confirm orders are executing
☐ No unusual errors
☐ Let bot trade automatically
```

### **End of Day (After 4:00 PM):**
```
☐ All positions closed at 4:00 PM
☐ Review daily P&L
☐ Note any issues
☐ Check if $2,500 target hit
☐ Log results for next day
```

---

## **SUCCESS MILESTONES**

| Day | Goal | Status |
|-----|------|--------|
| **Day 1** | Get 2-3 winning trades | |
| **Day 2** | Hit 55% win rate | |
| **Day 3** | Reach $2,500 profit ✅ | |
| **Day 4-10** | Complete Phase 2 | |
| **Day 15** | Get FUNDED 🚀 | |

---

## **WHAT'S DIFFERENT FROM NINJATRADER BOT?**

| Feature | NinjaTrader | Python |
|---------|-------------|--------|
| Platform Required | Windows only | Any OS ✅ |
| Installation | Complex | Simple ✅ |
| Cloud VPS | Hard | Easy ✅ |
| 24/7 Running | Hard | Easy ✅ |
| Customization | Limited | Full ✅ |
| Free to Run | Yes | Yes ✅ |

---

## **NEXT STEPS**

1. ✅ Get FundedNext API key
2. ✅ Download `fundednext_bot.py`
3. ✅ Choose: Local or Cloud VPS
4. ✅ Install Python (if local)
5. ✅ Set API key
6. ✅ Run bot
7. ✅ Monitor trades
8. ✅ Hit $2,500 → Phase 1 Complete!
9. ✅ Run Phase 2 → Get Funded!

---

## **QUESTIONS?**

**Need help with:**
- Python installation? → See Python.org
- VPS setup? → DigitalOcean tutorials
- Bot configuration? → Edit the `.py` file
- API key? → FundedNext settings

**You've got this!** 🚀💎

---

*Last Updated: September 2026*
*Bot Version: 1.0*
