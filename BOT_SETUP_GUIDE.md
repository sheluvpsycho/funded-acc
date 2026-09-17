# 🚀 FundedNext Challenge Bot - Setup & Configuration Guide

## ✅ YOUR BOT SPECS

| Setting | Value |
|---------|-------|
| **Account Size** | $50,000 |
| **Daily Profit Target** | $2,500 (5%) |
| **Max Loss Limit** | $1,500 (3%) |
| **Platform** | NinjaTrader 8 |
| **Instruments** | MES, MNQ, MYM (Micro Contracts) |
| **Strategy** | Bidirectional (LONG + SHORT) |
| **Risk Per Trade** | $200 |
| **Max Positions** | 3 concurrent |

---

## 📥 INSTALLATION STEPS

### **Step 1: Import the Strategy into NinjaTrader**

1. **Open NinjaTrader 8**
2. Go to: `Tools → Import → NinjaScript`
3. Select `FundedNext_Challenge_Bot.cs`
4. Click **Compile** (wait for confirmation)
   - ✅ Should see "Compile successful"
   - ❌ If errors appear, check NinjaTrader version (needs v8.x)

### **Step 2: Add Strategy to Chart**

1. **Open a chart** (1-hour or 15-minute recommended)
2. Click **Strategies** button (left panel)
3. Search for `FundedNext_Challenge_Bot`
4. Click **Add Strategy**
5. Configure settings (see below)

### **Step 3: Connect to Your FundedNext Account**

1. **Log into your FundedNext NinjaTrader account**
2. **Verify connection:**
   - Check Account Balance shows $50,000
   - Confirm you can see MES, MNQ, MYM contracts
   - Test a manual order (then cancel it)

---

## ⚙️ BOT CONFIGURATION

### **Primary Settings**

```
Daily Profit Target:    $2,500  (5% of $50K account)
Max Daily Loss:         $1,500  (3% of $50K account)
Risk Per Trade:         $200    (Position sizing)
Max Open Positions:     3       (No more than 3 trades at once)
```

### **Entry Strategy Settings**

```
Fast Moving Average:    9 periods
Slow Moving Average:    21 periods
Breakout Threshold:     0.15% above/below
Price Confirmation:     Required (price above/below MAs)
```

### **Exit Strategy Settings**

```
Take Profit Points:     20 ticks (for MES/MNQ = ~$25 profit per tick)
Stop Loss Points:       15 ticks (automatic stop)
Trailing Stop:          10 ticks (locks in profits)
Session Close:          4:00 PM EST (auto-exit remaining positions)
```

### **Trading Hours**

```
Session Start:          9:30 AM EST
Session End:            4:00 PM EST
Last Entry Time:        3:30 PM EST (don't enter new trades last 30 mins)
```

---

## 🎯 HOW THE BOT WORKS

### **Entry Logic**

**LONG Entry:**
- Fast MA (9) crosses ABOVE Slow MA (21) by >0.15%
- Price is ABOVE both moving averages
- Bot enters 1 micro contract

**SHORT Entry:**
- Fast MA (9) crosses BELOW Slow MA (21) by >0.15%
- Price is BELOW both moving averages
- Bot enters 1 micro contract

### **Exit Logic**

**Take Profit:**
- Long: When price moves up 20 ticks
- Short: When price moves down 20 ticks
- Auto-exits for profit ✓

**Stop Loss:**
- Long: When price drops 15 ticks below entry
- Short: When price rises 15 ticks above entry
- Auto-exits to protect capital ✓

**Time-Based Exit:**
- ALL positions close at 3:59 PM EST
- No overnight holds
- Prevents gap risk ✓

**Profit Target Hit:**
- If daily profit reaches $2,500 → Bot STOPS and closes all trades
- Locks in winnings 💰

**Max Loss Hit:**
- If daily loss reaches -$1,500 → Bot STOPS and closes all trades
- Protects account ✓

---

## 📊 POSITION SIZING CALCULATION

**For MES (Micro S&P 500):**
- 1 tick = $1.25
- Stop Loss = 15 ticks = $18.75 per contract
- Risk per trade = $200
- **Contracts = $200 ÷ $18.75 = 10-11 contracts per trade**

**For MNQ (Micro NASDAQ):**
- 1 tick = $2.00
- Stop Loss = 15 ticks = $30 per contract
- Risk per trade = $200
- **Contracts = $200 ÷ $30 = 6-7 contracts per trade**

*Bot auto-calculates these - no manual math needed!*

---

## ⏱️ SAMPLE TRADING DAY

### **9:30 AM - Market Open**
- Bot scans for entry signals
- Moving averages align
- LONG entry triggered
- Position: 11 MES contracts

### **10:15 AM - Take Profit Hit**
- Price moves up 20 ticks
- Auto-exit LONG for +$275 profit
- Profit counter: $275 / $2,500

### **11:00 AM - Another Signal**
- Short signal triggered
- SHORT entry: 10 MES contracts
- Stop loss placed 15 ticks below

### **12:30 PM - Stop Hit**
- Price reverses against short
- Stop loss triggered
- Exit: -$188 loss
- Profit counter: $275 - $188 = $87 net

### **3:00 PM - Profit Target Hit**
- Series of winning trades builds momentum
- Daily profit reaches $2,500
- ✅ **BOT STOPS ALL TRADING**
- 🎉 **CHALLENGE COMPLETE FOR THE DAY!**

---

## 🚨 IMPORTANT RULES & LIMITS

### **✅ DO:**
- Run bot during market hours only (9:30 AM - 4:00 PM EST)
- Monitor positions every 30-60 minutes
- Keep max daily loss limit at $1,500
- Reset daily counters at market open
- Review trade logs for optimization

### **❌ DON'T:**
- Don't modify stop loss/take profit mid-trade
- Don't overtrade (bot limits to 3 open positions)
- Don't trade during news (high volatility kills bots)
- Don't use leverage beyond position sizing
- Don't leave bot running after 4:00 PM EST

### **⚠️ RISKS TO MONITOR:**
1. **Gap Risk** - Bot exits at close (prevents overnight gaps)
2. **Slippage** - Micro contracts have tight spreads
3. **Volatility** - News events can trigger stops
4. **Connection Issues** - Backup internet recommended

---

## 📈 PERFORMANCE TRACKING

### **Daily Metrics**
```
Target Profit:        $2,500
Target Win Rate:      55%+ (with bot entries)
Avg Trade Duration:   15-45 minutes
Max Drawdown/Day:     $1,500 (hard stop)
```

### **Weekly Goals**
```
Days to Profit Target: 3-4 days
Weekly Profit:        $7,500 - $10,000
Win Rate Target:      55%+
Consistency:          No consecutive loss days
```

### **Phase 1 Completion**
```
Need: $2,500 profit
Target: 3-5 trading days
Then: Move to Phase 2 ($1,000-$1,500 target)
```

---

## 🔧 TROUBLESHOOTING

### **Bot won't start:**
- Check compilation: `Tools → Compile Strategies`
- Verify NinjaTrader v8.x installed
- Restart NinjaTrader

### **Orders not executing:**
- Verify account is logged in
- Check order confirmation settings
- Ensure you have sufficient margin ($50K)

### **Wrong position size:**
- Check risk per trade: $200
- Verify contract specifications
- Recalculate: Risk ÷ (Ticks × Tick Value)

### **Missing fills:**
- Increase slippage tolerance
- Trade more liquid hours (10 AM - 3 PM)
- Reduce position size by 10%

---

## 💡 OPTIMIZATION TIPS

**If bot wins too much:**
- Increase stop loss to 20 ticks
- Raise profit target to 25 ticks
- Reduce position size

**If bot loses too much:**
- Tighter stop loss (12 ticks)
- Lower profit target (15 ticks)
- Add volatility filters (skip news times)

**If bot overtrades:**
- Reduce # of MA periods (7 & 14 instead of 9 & 21)
- Increase breakout threshold to 0.20%
- Add time-based filters

---

## 📋 COMPLIANCE CHECKLIST

Before going live:

- [ ] NinjaTrader 8 installed
- [ ] Strategy compiled successfully
- [ ] Account has $50,000 balance
- [ ] Connected to FundedNext broker
- [ ] Can trade MES, MNQ, MYM
- [ ] Time zones correct (EST)
- [ ] Stop loss/profit targets verified
- [ ] Position sizing calculated
- [ ] Paper trade for 1-2 days first
- [ ] Ready to go live!

---

## 🎯 NEXT STEPS

1. **Compile strategy** in NinjaTrader
2. **Paper trade** for 1-2 days (no real money)
3. **Verify profit/loss tracking** works correctly
4. **Go live** with small position sizes
5. **Monitor daily** - review logs at close
6. **Hit $2,500** - Complete Phase 1 ✅
7. **Phase 2** - Run same bot with lower targets

---

## 📞 SUPPORT

**If bot has issues:**
1. Check NinjaTrader Output window for error messages
2. Verify strategy compilation
3. Restart platform
4. Test with manual order first
5. Contact NinjaTrader support if persistent issues

**Good luck with your FundedNext challenge!** 🚀💎

---

*Last Updated: September 2026*
*Strategy: FundedNext Challenge Bot v1.0*
