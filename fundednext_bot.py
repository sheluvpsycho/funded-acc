#!/usr/bin/env python3
"""
FundedNext Challenge Bot - Automated Futures Trading
Account: $50,000 | Target: $2,500 | Max Loss: $1,500
Trades: MES, MNQ, MYM (Micro Contracts)
Strategy: Bidirectional with MA Crossover + Smart Risk Management
"""

import os
import sys
import json
import time
from datetime import datetime, time as dt_time
from typing import Dict, List, Optional
import requests
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('fundednext_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class FundedNextBot:
    """Automated trading bot for FundedNext challenges"""
    
    def __init__(self, 
                 api_key: str,
                 account_size: float = 50000,
                 daily_profit_target: float = 2500,
                 max_daily_loss: float = 1500,
                 risk_per_trade: float = 200):
        """
        Initialize the trading bot
        
        Args:
            api_key: FundedNext API key
            account_size: Starting account balance
            daily_profit_target: Daily profit goal
            max_daily_loss: Maximum daily loss limit
            risk_per_trade: Dollar amount to risk per trade
        """
        self.api_key = api_key
        self.account_size = account_size
        self.daily_profit_target = daily_profit_target
        self.max_daily_loss = max_daily_loss
        self.risk_per_trade = risk_per_trade
        
        # Trading state
        self.current_day_profit = 0.0
        self.current_day_loss = 0.0
        self.open_positions = []
        self.trade_history = []
        self.last_reset_time = datetime.now()
        
        # Trading parameters
        self.fast_ma_period = 9
        self.slow_ma_period = 21
        self.breakout_threshold = 0.0015  # 0.15%
        self.take_profit_points = 20  # ticks
        self.stop_loss_points = 15    # ticks
        
        # Trading hours (EST)
        self.session_start = dt_time(9, 30)
        self.session_end = dt_time(16, 0)
        self.no_entry_after = dt_time(15, 30)  # Last 30 mins
        
        # API endpoints (example - update with actual FundedNext endpoints)
        self.base_url = "https://api.fundednext.com/v1"
        self.headers = {"Authorization": f"Bearer {api_key}"}
        
        logger.info("=" * 70)
        logger.info("FundedNext Challenge Bot Initialized")
        logger.info(f"Account Size: ${account_size:,.2f}")
        logger.info(f"Daily Profit Target: ${daily_profit_target:,.2f}")
        logger.info(f"Max Daily Loss: ${max_daily_loss:,.2f}")
        logger.info(f"Risk Per Trade: ${risk_per_trade:,.2f}")
        logger.info("=" * 70)
    
    def is_trading_hours(self) -> bool:
        """Check if current time is within trading hours"""
        now = datetime.now().time()
        # Only trade Monday-Friday, 9:30 AM - 4:00 PM EST
        return self.session_start <= now <= self.session_end
    
    def can_enter_new_trade(self) -> bool:
        """Check if we can enter a new trade"""
        now = datetime.now().time()
        # Don't enter new trades in last 30 minutes
        return now < self.no_entry_after
    
    def is_new_trading_day(self) -> bool:
        """Check if it's a new trading day"""
        if datetime.now().date() != self.last_reset_time.date():
            return True
        return False
    
    def reset_daily_stats(self):
        """Reset daily profit/loss counters"""
        self.current_day_profit = 0.0
        self.current_day_loss = 0.0
        self.last_reset_time = datetime.now()
        logger.info(f"Daily stats reset at {self.last_reset_time}")
    
    def get_market_data(self, symbol: str, timeframe: str = "1m") -> Optional[Dict]:
        """
        Get market data for a symbol
        
        Args:
            symbol: Trading symbol (MES, MNQ, MYM)
            timeframe: Candle timeframe (1m, 5m, 15m, 1h)
            
        Returns:
            Dictionary with OHLCV data or None if error
        """
        try:
            endpoint = f"{self.base_url}/market/candles"
            params = {
                "symbol": symbol,
                "timeframe": timeframe,
                "limit": 50  # Last 50 candles for MA calculation
            }
            
            response = requests.get(
                endpoint,
                headers=self.headers,
                params=params,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching market data for {symbol}: {e}")
            return None
    
    def calculate_moving_averages(self, prices: List[float]) -> tuple:
        """
        Calculate fast and slow moving averages
        
        Args:
            prices: List of closing prices
            
        Returns:
            Tuple of (fast_ma, slow_ma)
        """
        if len(prices) < self.slow_ma_period:
            return None, None
        
        fast_ma = sum(prices[-self.fast_ma_period:]) / self.fast_ma_period
        slow_ma = sum(prices[-self.slow_ma_period:]) / self.slow_ma_period
        
        return fast_ma, slow_ma
    
    def check_long_signal(self, fast_ma: float, slow_ma: float, current_price: float) -> bool:
        """
        Check if we should enter LONG position
        
        Conditions:
        - Fast MA > Slow MA (by breakout threshold)
        - Price > Fast MA (confirmation)
        """
        if fast_ma is None or slow_ma is None:
            return False
        
        # Fast MA above slow MA by threshold
        if fast_ma > slow_ma * (1 + self.breakout_threshold):
            # Price confirmation
            if current_price > fast_ma:
                return True
        
        return False
    
    def check_short_signal(self, fast_ma: float, slow_ma: float, current_price: float) -> bool:
        """
        Check if we should enter SHORT position
        
        Conditions:
        - Fast MA < Slow MA (by breakout threshold)
        - Price < Fast MA (confirmation)
        """
        if fast_ma is None or slow_ma is None:
            return False
        
        # Fast MA below slow MA by threshold
        if fast_ma < slow_ma * (1 - self.breakout_threshold):
            # Price confirmation
            if current_price < fast_ma:
                return True
        
        return False
    
    def calculate_position_size(self, symbol: str) -> int:
        """
        Calculate optimal position size based on risk per trade
        
        Args:
            symbol: Trading symbol (MES, MNQ, MYM)
            
        Returns:
            Number of contracts to trade
        """
        # Tick values for micro contracts
        tick_values = {
            "MES": 1.25,   # Micro E-mini S&P 500
            "MNQ": 2.00,   # Micro E-mini NASDAQ
            "MYM": 0.50,   # Micro E-mini Dow
        }
        
        tick_value = tick_values.get(symbol, 1.25)
        
        # Risk = Stop Loss Points × Tick Value × Contracts
        # Contracts = Risk / (Stop Loss Points × Tick Value)
        risk_per_contract = self.stop_loss_points * tick_value
        position_size = max(1, int(self.risk_per_trade / risk_per_contract))
        
        return position_size
    
    def place_order(self, 
                   symbol: str,
                   direction: str,
                   quantity: int,
                   entry_price: float) -> Optional[str]:
        """
        Place a trading order
        
        Args:
            symbol: Trading symbol
            direction: "BUY" or "SELL"
            quantity: Number of contracts
            entry_price: Entry price
            
        Returns:
            Order ID or None if failed
        """
        try:
            endpoint = f"{self.base_url}/orders"
            
            payload = {
                "symbol": symbol,
                "direction": direction,
                "quantity": quantity,
                "order_type": "MARKET",
                "time_in_force": "DAY"
            }
            
            response = requests.post(
                endpoint,
                headers=self.headers,
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            
            order_data = response.json()
            order_id = order_data.get("order_id")
            
            # Log the trade
            trade = {
                "timestamp": datetime.now().isoformat(),
                "symbol": symbol,
                "direction": direction,
                "quantity": quantity,
                "entry_price": entry_price,
                "order_id": order_id
            }
            self.trade_history.append(trade)
            
            logger.info(f"ORDER PLACED: {direction} {quantity} {symbol} @ {entry_price}")
            logger.info(f"Order ID: {order_id}")
            
            return order_id
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error placing order: {e}")
            return None
    
    def close_position(self, order_id: str, reason: str) -> bool:
        """
        Close an existing position
        
        Args:
            order_id: ID of the position to close
            reason: Reason for closing (TP, SL, etc.)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            endpoint = f"{self.base_url}/orders/{order_id}/close"
            
            response = requests.post(
                endpoint,
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            
            logger.info(f"POSITION CLOSED: {order_id} - Reason: {reason}")
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error closing position: {e}")
            return False
    
    def manage_positions(self, symbol: str, current_price: float):
        """
        Manage existing open positions
        
        Args:
            symbol: Trading symbol
            current_price: Current market price
        """
        for position in self.open_positions[:]:
            entry_price = position["entry_price"]
            direction = position["direction"]
            order_id = position["order_id"]
            quantity = position["quantity"]
            
            # Calculate P&L for this position
            if direction == "BUY":
                pnl = (current_price - entry_price) * quantity * 12.5  # MES multiplier
                
                # Take Profit
                if current_price >= entry_price + (self.take_profit_points * 0.25):
                    self.close_position(order_id, "TAKE_PROFIT")
                    self.current_day_profit += abs(pnl)
                    self.open_positions.remove(position)
                    
                # Stop Loss
                elif current_price <= entry_price - (self.stop_loss_points * 0.25):
                    self.close_position(order_id, "STOP_LOSS")
                    self.current_day_loss += abs(pnl)
                    self.open_positions.remove(position)
            
            elif direction == "SELL":
                pnl = (entry_price - current_price) * quantity * 12.5
                
                # Take Profit
                if current_price <= entry_price - (self.take_profit_points * 0.25):
                    self.close_position(order_id, "TAKE_PROFIT")
                    self.current_day_profit += abs(pnl)
                    self.open_positions.remove(position)
                    
                # Stop Loss
                elif current_price >= entry_price + (self.stop_loss_points * 0.25):
                    self.close_position(order_id, "STOP_LOSS")
                    self.current_day_loss += abs(pnl)
                    self.open_positions.remove(position)
    
    def check_limits(self) -> bool:
        """
        Check if we've hit profit target or max loss
        
        Returns:
            False if limits hit (should stop trading), True otherwise
        """
        if self.current_day_profit >= self.daily_profit_target:
            logger.warning(f"✓ PROFIT TARGET HIT: ${self.current_day_profit:,.2f}")
            return False
        
        if self.current_day_loss <= -self.max_daily_loss:
            logger.warning(f"✗ MAX LOSS REACHED: ${self.current_day_loss:,.2f}")
            return False
        
        return True
    
    def run_trading_cycle(self, symbol: str = "MNQ"):
        """
        Execute one complete trading cycle
        
        Args:
            symbol: Trading symbol to trade
        """
        try:
            # Check if new trading day
            if self.is_new_trading_day():
                self.reset_daily_stats()
            
            # Check if trading hours
            if not self.is_trading_hours():
                logger.info("Outside trading hours, waiting...")
                return
            
            # Get market data
            market_data = self.get_market_data(symbol)
            if not market_data:
                logger.warning("Could not fetch market data")
                return
            
            # Extract price data
            candles = market_data.get("candles", [])
            if len(candles) < self.slow_ma_period:
                logger.warning("Insufficient candle data")
                return
            
            prices = [float(candle["close"]) for candle in candles]
            current_price = prices[-1]
            
            # Calculate moving averages
            fast_ma, slow_ma = self.calculate_moving_averages(prices)
            
            if fast_ma is None or slow_ma is None:
                logger.warning("Could not calculate moving averages")
                return
            
            logger.info(f"\n{'='*60}")
            logger.info(f"Trading Cycle: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            logger.info(f"Symbol: {symbol} | Price: {current_price:.2f}")
            logger.info(f"Fast MA(9): {fast_ma:.2f} | Slow MA(21): {slow_ma:.2f}")
            logger.info(f"Daily P&L: ${self.current_day_profit - abs(self.current_day_loss):,.2f}")
            logger.info(f"Progress: ${self.current_day_profit:,.2f} / ${self.daily_profit_target:,.2f}")
            logger.info(f"{'='*60}\n")
            
            # Check limits
            if not self.check_limits():
                logger.warning("Daily trading limits reached, stopping...")
                return
            
            # Manage existing positions
            self.manage_positions(symbol, current_price)
            
            # Check for new entry signals (only if can enter)
            if self.can_enter_new_trade() and len(self.open_positions) < 3:
                if self.check_long_signal(fast_ma, slow_ma, current_price):
                    position_size = self.calculate_position_size(symbol)
                    order_id = self.place_order(symbol, "BUY", position_size, current_price)
                    
                    if order_id:
                        self.open_positions.append({
                            "order_id": order_id,
                            "symbol": symbol,
                            "direction": "BUY",
                            "entry_price": current_price,
                            "quantity": position_size
                        })
                
                elif self.check_short_signal(fast_ma, slow_ma, current_price):
                    position_size = self.calculate_position_size(symbol)
                    order_id = self.place_order(symbol, "SELL", position_size, current_price)
                    
                    if order_id:
                        self.open_positions.append({
                            "order_id": order_id,
                            "symbol": symbol,
                            "direction": "SELL",
                            "entry_price": current_price,
                            "quantity": position_size
                        })
        
        except Exception as e:
            logger.error(f"Error in trading cycle: {e}", exc_info=True)
    
    def run_live(self, symbols: List[str] = None, cycle_interval: int = 60):
        """
        Run the bot continuously
        
        Args:
            symbols: List of symbols to trade (default: MNQ)
            cycle_interval: Seconds between trading cycles
        """
        if symbols is None:
            symbols = ["MNQ"]
        
        logger.info(f"Starting live trading for: {', '.join(symbols)}")
        logger.info(f"Cycle interval: {cycle_interval} seconds")
        
        try:
            while True:
                for symbol in symbols:
                    self.run_trading_cycle(symbol)
                
                # Wait before next cycle
                logger.info(f"Waiting {cycle_interval}s before next cycle...")
                time.sleep(cycle_interval)
        
        except KeyboardInterrupt:
            logger.info("Bot stopped by user")
        except Exception as e:
            logger.error(f"Fatal error: {e}", exc_info=True)


def main():
    """Main entry point"""
    
    # Get API key from environment
    api_key = os.getenv("FUNDEDNEXT_API_KEY")
    if not api_key:
        logger.error("FUNDEDNEXT_API_KEY environment variable not set")
        sys.exit(1)
    
    # Initialize bot
    bot = FundedNextBot(
        api_key=api_key,
        account_size=50000,
        daily_profit_target=2500,
        max_daily_loss=1500,
        risk_per_trade=200
    )
    
    # Start trading
    bot.run_live(symbols=["MNQ"], cycle_interval=60)


if __name__ == "__main__":
    main()
