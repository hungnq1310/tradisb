import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

class OrderType(Enum):
    BUY = "BUY"
    SELL = "SELL"

class OrderStatus(Enum):
    PENDING = "PENDING"
    FILLED = "FILLED"
    CANCELLED = "CANCELLED"

@dataclass
class PseudoOrder:
    id: str
    symbol: str
    order_type: OrderType
    quantity: float
    price: float
    timestamp: datetime
    status: OrderStatus = OrderStatus.PENDING
    fill_price: Optional[float] = None
    fill_timestamp: Optional[datetime] = None

@dataclass
class TradingSignal:
    symbol: str
    signal_type: str  # "BUY" or "SELL"
    price: float
    change_percent: float
    volume: float
    timestamp: datetime
    confidence: float = 0.0  # 0.0 to 1.0

class TradingSignalValidator:
    def __init__(self, binance_client):
        self.binance_client = binance_client
        self.orders: List[PseudoOrder] = []
        self.signals: List[TradingSignal] = []
        
    def validate_signal_criteria(self, ticker_data: Dict) -> bool:
        """Validate if ticker data meets trading signal criteria"""
        try:
            change_percent = float(ticker_data['priceChangePercent'])
            volume = float(ticker_data['volume'])
            
            # Signal criteria: >5% change and volume > 1000
            return abs(change_percent) > 5.0 and volume > 1000
        except (KeyError, ValueError):
            return False
    
    def generate_trading_signal(self, ticker_data: Dict) -> Optional[TradingSignal]:
        """Generate a trading signal from ticker data"""
        if not self.validate_signal_criteria(ticker_data):
            return None
            
        change_percent = float(ticker_data['priceChangePercent'])
        signal_type = "BUY" if change_percent > 0 else "SELL"
        confidence = min(abs(change_percent) / 10.0, 1.0)  # Max confidence at 10% change
        
        signal = TradingSignal(
            symbol=ticker_data['symbol'],
            signal_type=signal_type,
            price=float(ticker_data['lastPrice']),
            change_percent=change_percent,
            volume=float(ticker_data['volume']),
            timestamp=datetime.now(),
            confidence=confidence
        )
        
        self.signals.append(signal)
        return signal
    
    def create_pseudo_order(self, signal: TradingSignal, quantity: float) -> PseudoOrder:
        """Create a pseudo order based on trading signal"""
        order_id = f"ORDER_{len(self.orders) + 1}_{signal.symbol}_{int(datetime.now().timestamp())}"
        
        order = PseudoOrder(
            id=order_id,
            symbol=signal.symbol,
            order_type=OrderType(signal.signal_type),
            quantity=quantity,
            price=signal.price,
            timestamp=datetime.now()
        )
        
        self.orders.append(order)
        return order
    
    def simulate_order_fill(self, order: PseudoOrder, market_price: float) -> bool:
        """Simulate order execution based on market conditions"""
        if order.status != OrderStatus.PENDING:
            return False
            
        # Simple fill logic: fill if price is within 1% of order price
        price_diff_percent = abs(market_price - order.price) / order.price * 100
        
        if price_diff_percent <= 1.0:  # Fill within 1% of order price
            order.status = OrderStatus.FILLED
            order.fill_price = market_price
            order.fill_timestamp = datetime.now()
            return True
        
        # Cancel order if it's older than 5 minutes
        if datetime.now() - order.timestamp > timedelta(minutes=5):
            order.status = OrderStatus.CANCELLED
            
        return False
    
    def get_active_signals(self, max_age_minutes: int = 10) -> List[TradingSignal]:
        """Get signals within specified time window"""
        cutoff_time = datetime.now() - timedelta(minutes=max_age_minutes)
        return [s for s in self.signals if s.timestamp > cutoff_time]
    
    def get_pending_orders(self) -> List[PseudoOrder]:
        """Get all pending orders"""
        return [o for o in self.orders if o.status == OrderStatus.PENDING]