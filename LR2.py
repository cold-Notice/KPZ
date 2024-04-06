import pandas as pd
from binance.client import Client
from binance.exceptions import BinanceAPIException
from datetime import datetime, timedelta

# Функция для расчета индекса относительной силы (RSI)
def calculate_rsi(prices, period):
    deltas = prices.diff()  # Разность между последовательными ценами
    gains = deltas.where(deltas > 0, 0)  # Только приросты
    losses = -deltas.where(deltas < 0, 0)  # Только потери
    avg_gain = gains.rolling(window=period, min_periods=1).mean()  # Средний прирост
    avg_loss = losses.rolling(window=period, min_periods=1).mean()  # Средняя потеря
    rs = avg_gain / avg_loss  # Отношение среднего прироста к средней потере
    rsi = 100 - (100 / (1 + rs))  # Расчет RSI
    return rsi

# Получение данных RSI для актива
def get_rsi_data(asset, periods):
    try:
        client = Client()
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(days=1)
        # Запрос исторических данных
        klines = client.get_historical_klines(
            symbol=asset,
            interval=Client.KLINE_INTERVAL_1MINUTE,
            start_str=start_time.strftime("%Y-%m-%d %H:%M:%S"),
            end_str=end_time.strftime("%Y-%m-%d %H:%M:%S")
        )
        # Создание DataFrame из полученных данных
        df = pd.DataFrame(klines, columns=['time', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])
        df['time'] = pd.to_datetime(df['time'], unit='ms')
        df['close'] = df['close'].astype(float)
        
        result = pd.DataFrame({'time': df['time']})
        for period in periods:
            rsi_values = calculate_rsi(df['close'], period)  # Расчет RSI для каждого периода
            result[f'RSI_{period}'] = rsi_values
        return result
    except BinanceAPIException as e:
        print(f"Произошла ошибка: {e}")
        return pd.DataFrame()

asset = "BTCUSDT"
periods = [14, 27, 100]
rsi_data = get_rsi_data(asset, periods)
print(rsi_data)
