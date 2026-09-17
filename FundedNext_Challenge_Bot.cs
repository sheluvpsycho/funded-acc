// FundedNext Challenge Bot - NinjaTrader Strategy
// Account: $50,000 | Target: $2,500 profit | Max Loss: $1,500
// Trades: MES, MNQ, MYM (Micro Contracts)
// Strategy: Bidirectional (LONG + SHORT) with Smart Entry & Exit

#region Using declarations
using System;
using System.ComponentModel;
using System.ComponentModel.DataAnnotations;
using cbi = Cbi;
using Cbi;
using Cbi.ToolStrip;
using NinjaTrader.Cbi;
using NinjaTrader.Gui;
using NinjaTrader.Gui.Tools;
using NinjaTrader.Data;
using NinjaTrader.NinjaScript;
using NinjaTrader.Core.FloatingPoint;
using NinjaTrader.Instrument;
#endregion

namespace NinjaTrader.NinjaScript.Strategies
{
    public class FundedNextChallengeBot : Strategy
    {
        #region Variables
        
        // Account Risk Management
        private double dailyProfitTarget = 2500;      // Phase 1 target
        private double maxLossLimit = 1500;            // Hard stop loss
        private double accountSize = 50000;            // Starting capital
        
        // Position Management
        private double riskPerTrade = 200;             // $ risk per trade
        private int maxOpenPositions = 3;              // Max concurrent trades
        private int positionSize = 1;                  // Contracts per trade
        
        // Trading Session Times (US Market Hours)
        private int sessionStartHour = 9;              // 9:30 AM EST
        private int sessionStartMinute = 30;
        private int sessionEndHour = 16;               // 4:00 PM EST
        private int sessionEndMinute = 0;
        
        // Profit & Loss Tracking
        private double currentDayProfit = 0;
        private double currentDayLoss = 0;
        private double accountEquity = 0;
        private DateTime lastResetTime;
        
        // Entry Signals
        private bool useMovingAverages = true;
        private int fastMA = 9;
        private int slowMA = 21;
        private double breakoutPercent = 0.15;        // 0.15% breakout threshold
        
        // Exit Rules
        private double takeProfitPoints = 20;          // Profit in ticks
        private double stopLossPoints = 15;            // Stop in ticks
        private double trailingStopPoints = 10;        // Trailing stop
        
        #endregion
        
        protected override void OnStateChange()
        {
            if (State == State.SetDefaults)
            {
                Description = "FundedNext Challenge Bot - $2,500 Target / $1,500 Max Loss";
                Name = "FundedNext_Challenge_Bot";
                
                // Strategy settings
                Calculate = Calculate.OnBarClose;
                EntriesPerDirection = 1;
                EntryHandling = EntryHandling.AllEntries;
                IsExitOnSessionCloseStrategy = true;
                ExitOnSessionCloseSeconds = 30;
                IsFillLimitOnSessionCloseStrategy = false;
                DefaultQuantity = 1;
                TraceOrders = true;
                RealtimeErrorHandling = RealtimeErrorHandling.StopCancelClose;
                StopTargetHandling = StopTargetHandling.PerEntryExecution;
                BarsRequiredToTrade = 20;
                
                // Add default input parameters
                AddParameter("DailyTarget", 2500);
                AddParameter("MaxLoss", 1500);
                AddParameter("RiskPerTrade", 200);
                
                IsOverlay = false;
                DisplayInDataBox = true;
            }
            else if (State == State.Configure)
            {
                ClearOutputWindow();
                Print("=== FundedNext Challenge Bot Initialized ===");
                Print($"Account Size: ${accountSize}");
                Print($"Daily Profit Target: ${dailyProfitTarget}");
                Print($"Max Loss Limit: ${maxLossLimit}");
                Print($"Risk Per Trade: ${riskPerTrade}");
                Print("================================================");
                
                lastResetTime = DateTime.Now;
            }
        }
        
        protected override void OnBarUpdate()
        {
            // Skip if not enough bars
            if (CurrentBar < BarsRequiredToTrade)
                return;
                
            // Check if we're in valid trading hours
            if (!IsValidTradingHour())
                return;
                
            // Reset daily stats at market open
            if (IsNewTradingDay())
            {
                currentDayProfit = 0;
                currentDayLoss = 0;
                lastResetTime = DateTime.Now;
            }
            
            // Update account equity
            accountEquity = GetAccountEquity();
            
            // Check if we've hit profit target or max loss
            if (currentDayProfit >= dailyProfitTarget)
            {
                Print($"✓ PROFIT TARGET HIT: ${currentDayProfit}");
                CloseAllPositions("Profit Target Reached");
                return;
            }
            
            if (currentDayLoss <= -maxLossLimit)
            {
                Print($"✗ MAX LOSS REACHED: ${currentDayLoss}");
                CloseAllPositions("Max Loss Limit Hit");
                return;
            }
            
            // Exit any losing trades early to preserve capital
            ManageExistingPositions();
            
            // Check open position count
            if (Position.MarketPosition == MarketPosition.Flat && GetOpenPositionCount() < maxOpenPositions)
            {
                // Generate trading signals
                if (ShouldEnterLong())
                {
                    EnterLongPosition();
                }
                else if (ShouldEnterShort())
                {
                    EnterShortPosition();
                }
            }
            
            // Update display
            DrawStrategyStatus();
        }
        
        #region Entry Logic
        
        private bool ShouldEnterLong()
        {
            // Moving Average Crossover
            if (useMovingAverages)
            {
                double fastAvg = SMA(Close, fastMA)[0];
                double slowAvg = SMA(Close, slowMA)[0];
                
                if (fastAvg > slowAvg * (1 + breakoutPercent / 100))
                {
                    // Additional confirmation: price above both MAs
                    if (Close[0] > fastAvg)
                    {
                        return true;
                    }
                }
            }
            
            return false;
        }
        
        private bool ShouldEnterShort()
        {
            // Moving Average Crossover (Short)
            if (useMovingAverages)
            {
                double fastAvg = SMA(Close, fastMA)[0];
                double slowAvg = SMA(Close, slowMA)[0];
                
                if (fastAvg < slowAvg * (1 - breakoutPercent / 100))
                {
                    // Additional confirmation: price below both MAs
                    if (Close[0] < fastAvg)
                    {
                        return true;
                    }
                }
            }
            
            return false;
        }
        
        private void EnterLongPosition()
        {
            // Calculate position size based on risk
            int contracts = (int)Math.Max(1, Math.Floor(riskPerTrade / (stopLossPoints * 12.5)));
            
            EnterLong(contracts, "Long Entry");
            Print($"LONG: Entered {contracts} contract(s) at {Close[0]}");
        }
        
        private void EnterShortPosition()
        {
            // Calculate position size based on risk
            int contracts = (int)Math.Max(1, Math.Floor(riskPerTrade / (stopLossPoints * 12.5)));
            
            EnterShort(contracts, "Short Entry");
            Print($"SHORT: Entered {contracts} contract(s) at {Close[0]}");
        }
        
        #endregion
        
        #region Exit Logic
        
        private void ManageExistingPositions()
        {
            if (Position.MarketPosition == MarketPosition.Long)
            {
                // Take Profit
                if (Close[0] >= Position.AvgPrice + (takeProfitPoints * 0.25))
                {
                    ExitLong(0, "TP Long");
                }
                
                // Stop Loss
                if (Close[0] <= Position.AvgPrice - (stopLossPoints * 0.25))
                {
                    ExitLong(0, "SL Long");
                }
            }
            else if (Position.MarketPosition == MarketPosition.Short)
            {
                // Take Profit
                if (Close[0] <= Position.AvgPrice - (takeProfitPoints * 0.25))
                {
                    ExitShort(0, "TP Short");
                }
                
                // Stop Loss
                if (Close[0] >= Position.AvgPrice + (stopLossPoints * 0.25))
                {
                    ExitShort(0, "SL Short");
                }
            }
        }
        
        private void CloseAllPositions(string reason)
        {
            if (Position.MarketPosition == MarketPosition.Long)
            {
                ExitLong(0, reason);
            }
            else if (Position.MarketPosition == MarketPosition.Short)
            {
                ExitShort(0, reason);
            }
        }
        
        #endregion
        
        #region Helper Methods
        
        private bool IsValidTradingHour()
        {
            TimeSpan currentTime = DateTime.Now.TimeOfDay;
            TimeSpan sessionStart = new TimeSpan(sessionStartHour, sessionStartMinute, 0);
            TimeSpan sessionEnd = new TimeSpan(sessionEndHour, sessionEndMinute, 0);
            
            // Don't trade near close (last 30 mins)
            if (currentTime >= new TimeSpan(15, 30, 0))
                return false;
                
            return currentTime >= sessionStart && currentTime <= sessionEnd;
        }
        
        private bool IsNewTradingDay()
        {
            return DateTime.Now.Date > lastResetTime.Date;
        }
        
        private double GetAccountEquity()
        {
            try
            {
                return SystemPerformance.AllTrades.TradesPerformance.Percent;
            }
            catch
            {
                return 0;
            }
        }
        
        private int GetOpenPositionCount()
        {
            return Math.Abs(Position.Quantity);
        }
        
        private void DrawStrategyStatus()
        {
            // Draw P&L on chart
            AddChartString(Close[0], $"Profit: ${currentDayProfit:F2} | Loss: ${currentDayLoss:F2}");
        }
        
        #endregion
        
        protected override void OnExecutionUpdate(Execution execution, string executionId, double price, int quantity,
            MarketPosition marketPosition, string orderId, DateTime time)
        {
            if (execution.Order != null && execution.Order.OrderState == OrderState.Filled)
            {
                // Track P&L
                double profitLoss = (double)execution.Order.AverageFillPrice * quantity;
                
                if (profitLoss > 0)
                    currentDayProfit += profitLoss;
                else
                    currentDayLoss += profitLoss;
                    
                Print($"{execution.Order.Name}: {execution.Order.OrderAction} {quantity} @ {price}");
            }
        }
    }
}
