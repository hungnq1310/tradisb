import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from src.schema import (
    TradingSignalValidator, TradingSignal, PseudoOrder, 
    OrderType, OrderStatus
)

@pytest.fixture
def mock_binance_client():
    """Mock Binance client for testing"""
    mock_client = Mock()
    mock_client.get_ticker.return_value = [
        {
            'symbol': 'BTCUSDT',
            'lastPrice': '50000.00',
            'priceChangePercent': '5.5',
            'volume': '2000.0'
        },
        {
            'symbol': 'ETHUSDT', 
            'lastPrice': '3000.00',
            'priceChangePercent': '-3.2',
            'volume': '500.0'  # Low volume, shouldn't generate signal
        }
    ]
    return mock_client

@pytest.fixture
def trading_validator(mock_binance_client):
    """Create TradingSignalValidator instance for testing"""
    return TradingSignalValidator(mock_binance_client)

@pytest.fixture
def sample_ticker_data():
    """Sample ticker data for testing"""
    return {
        'symbol': 'BTCUSDT',
        'lastPrice': '50000.00',
        'priceChangePercent': '7.5',
        'volume': '5000.0'
    }

@pytest.fixture
def sample_low_volume_ticker():
    """Sample ticker with low volume"""
    return {
        'symbol': 'LOWUSDT',
        'lastPrice': '1.00',
        'priceChangePercent': '8.0',
        'volume': '500.0'  # Below threshold
    }

class TestTradingSignalValidator:
    
    def test_validate_signal_criteria_valid(self, trading_validator, sample_ticker_data):
        """Test signal validation with valid criteria"""
        result = trading_validator.validate_signal_criteria(sample_ticker_data)
        assert result is True
    
    def test_validate_signal_criteria_low_change(self, trading_validator):
        """Test signal validation with low price change"""
        ticker_data = {
            'symbol': 'BTCUSDT',
            'lastPrice': '50000.00',
            'priceChangePercent': '2.0',  # Below 5% threshold
            'volume': '5000.0'
        }
        result = trading_validator.validate_signal_criteria(ticker_data)
        assert result is False
    
    def test_validate_signal_criteria_low_volume(self, trading_validator, sample_low_volume_ticker):
        """Test signal validation with low volume"""
        result = trading_validator.validate_signal_criteria(sample_low_volume_ticker)
        assert result is False
    
    def test_validate_signal_criteria_missing_data(self, trading_validator):
        """Test signal validation with missing data"""
        ticker_data = {'symbol': 'BTCUSDT'}  # Missing required fields
        result = trading_validator.validate_signal_criteria(ticker_data)
        assert result is False
    
    def test_generate_trading_signal_buy(self, trading_validator, sample_ticker_data):
        """Test generating BUY trading signal"""
        signal = trading_validator.generate_trading_signal(sample_ticker_data)
        
        assert signal is not None
        assert signal.symbol == 'BTCUSDT'
        assert signal.signal_type == 'BUY'
        assert signal.price == 50000.0
        assert signal.change_percent == 7.5
        assert signal.confidence == 0.75  # 7.5% / 10% = 0.75
        assert len(trading_validator.signals) == 1
    
    def test_generate_trading_signal_sell(self, trading_validator):
        """Test generating SELL trading signal"""
        ticker_data = {
            'symbol': 'ETHUSDT',
            'lastPrice': '3000.00',
            'priceChangePercent': '-6.0',  # Negative for SELL signal
            'volume': '5000.0'
        }
        
        signal = trading_validator.generate_trading_signal(ticker_data)
        
        assert signal is not None
        assert signal.signal_type == 'SELL'
        assert signal.change_percent == -6.0
        assert signal.confidence == 0.6  # 6.0% / 10% = 0.6
    
    def test_generate_trading_signal_invalid(self, trading_validator, sample_low_volume_ticker):
        """Test that invalid ticker data doesn't generate signal"""
        signal = trading_validator.generate_trading_signal(sample_low_volume_ticker)
        assert signal is None
        assert len(trading_validator.signals) == 0
    
    def test_create_pseudo_order(self, trading_validator, sample_ticker_data):
        """Test creating pseudo order from signal"""
        signal = trading_validator.generate_trading_signal(sample_ticker_data)
        order = trading_validator.create_pseudo_order(signal, 0.001)
        
        assert order.symbol == 'BTCUSDT'
        assert order.order_type == OrderType.BUY
        assert order.quantity == 0.001
        assert order.price == 50000.0
        assert order.status == OrderStatus.PENDING
        assert order.id.startswith('ORDER_')
        assert len(trading_validator.orders) == 1
    
    def test_simulate_order_fill_success(self, trading_validator, sample_ticker_data):
        """Test successful order fill simulation"""
        signal = trading_validator.generate_trading_signal(sample_ticker_data)
        order = trading_validator.create_pseudo_order(signal, 0.001)
        
        # Market price within 1% of order price
        market_price = 50250.0  # 0.5% difference
        
        filled = trading_validator.simulate_order_fill(order, market_price)
        
        assert filled is True
        assert order.status == OrderStatus.FILLED
        assert order.fill_price == market_price
        assert order.fill_timestamp is not None
    
    def test_simulate_order_fill_price_gap(self, trading_validator, sample_ticker_data):
        """Test order fill failure due to price gap"""
        signal = trading_validator.generate_trading_signal(sample_ticker_data)
        order = trading_validator.create_pseudo_order(signal, 0.001)
        
        # Market price outside 1% range
        market_price = 51000.0  # 2% difference
        
        filled = trading_validator.simulate_order_fill(order, market_price)
        
        assert filled is False
        assert order.status == OrderStatus.PENDING
        assert order.fill_price is None
    
    def test_simulate_order_fill_timeout(self, trading_validator, sample_ticker_data):
        """Test order cancellation due to timeout"""
        signal = trading_validator.generate_trading_signal(sample_ticker_data)
        order = trading_validator.create_pseudo_order(signal, 0.001)
        
        # Simulate old order (6 minutes ago)
        order.timestamp = datetime.now() - timedelta(minutes=6)
        
        market_price = 51000.0
        filled = trading_validator.simulate_order_fill(order, market_price)
        
        assert filled is False
        assert order.status == OrderStatus.CANCELLED
    
    def test_get_active_signals(self, trading_validator, sample_ticker_data):
        """Test retrieving active signals within time window"""
        # Generate signal
        signal = trading_validator.generate_trading_signal(sample_ticker_data)
        
        # Add old signal
        old_signal = TradingSignal(
            symbol='OLDUSDT',
            signal_type='BUY',
            price=1000.0,
            change_percent=5.0,
            volume=2000.0,
            timestamp=datetime.now() - timedelta(minutes=15)
        )
        trading_validator.signals.append(old_signal)
        
        active_signals = trading_validator.get_active_signals(max_age_minutes=10)
        
        assert len(active_signals) == 1
        assert active_signals[0].symbol == 'BTCUSDT'
    
    def test_get_pending_orders(self, trading_validator, sample_ticker_data):
        """Test retrieving pending orders"""
        signal = trading_validator.generate_trading_signal(sample_ticker_data)
        order1 = trading_validator.create_pseudo_order(signal, 0.001)
        order2 = trading_validator.create_pseudo_order(signal, 0.002)
        
        # Fill one order
        order1.status = OrderStatus.FILLED
        
        pending_orders = trading_validator.get_pending_orders()
        
        assert len(pending_orders) == 1
        assert pending_orders[0].id == order2.id
        assert pending_orders[0].status == OrderStatus.PENDING

class TestIntegration:
    """Integration tests for the complete workflow"""
    
    @patch('src.schema.datetime')
    def test_complete_trading_workflow(self, mock_datetime, trading_validator, sample_ticker_data):
        """Test complete workflow from signal generation to order execution"""
        # Mock datetime to control timestamps
        base_time = datetime(2023, 1, 1, 12, 0, 0)
        mock_datetime.now.return_value = base_time
        
        # 1. Generate signal
        signal = trading_validator.generate_trading_signal(sample_ticker_data)
        assert signal is not None
        
        # 2. Create order
        order = trading_validator.create_pseudo_order(signal, 0.001)
        assert order.status == OrderStatus.PENDING
        
        # 3. Simulate market movement and fill
        market_price = 50200.0  # 0.4% difference
        filled = trading_validator.simulate_order_fill(order, market_price)
        assert filled is True
        assert order.status == OrderStatus.FILLED
        
        # 4. Verify final state
        assert len(trading_validator.signals) == 1
        assert len(trading_validator.orders) == 1
        assert len(trading_validator.get_pending_orders()) == 0

@pytest.mark.parametrize("change_percent,volume,expected", [
    (6.0, 2000.0, True),    # Valid signal
    (4.0, 2000.0, False),   # Low change
    (6.0, 500.0, False),    # Low volume
    (-7.0, 3000.0, True),   # Valid sell signal
    (0.0, 5000.0, False),   # No change
])
def test_signal_validation_parametrized(trading_validator, change_percent, volume, expected):
    """Parametrized test for signal validation"""
    ticker_data = {
        'symbol': 'TESTUSDT',
        'lastPrice': '1000.00',
        'priceChangePercent': str(change_percent),
        'volume': str(volume)
    }
    
    result = trading_validator.validate_signal_criteria(ticker_data)
    assert result == expected