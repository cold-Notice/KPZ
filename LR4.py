import pandas as pd
import ta
import matplotlib.pyplot as plt
from binance.client import Client
from matplotlib.dates import DateFormatter

def fetch_binance_data(symbol, interval, start_time, end_time):
    """Загрузка исторических данных с Binance."""
    client = Client()
    k_lines = client.get_historical_klines(
        symbol=symbol,
        interval=interval,
        start_str=start_time,
        end_str=end_time
    )
    return k_lines

def calculate_rsi(df, periods):
    """Расчет индекса относительной силы (RSI) для заданных периодов."""
    for period in periods:
        rsi_indicator = ta.momentum.RSIIndicator(df['close'], window=period)
        df[f'RSI_{period}'] = rsi_indicator.rsi()
    return df

def visualize_data(df, periods):
    """Визуализация данных о цене закрытия и индикаторов RSI."""
    plt.figure(figsize=(14, 10))
    # Визуализация цены закрытия
    plt.subplot(len(periods) + 1, 1, 1)
    plt.plot(df['time'], df['close'], label='Цена закрытия')
    plt.title('Цена закрытия')
    plt.ylabel('Цена')

    # Визуализация RSI для каждого периода
    for i, period in enumerate(periods):
        plt.subplot(len(periods) + 1, 1, i + 2)
        plt.plot(df['time'], df[f'RSI_{period}'], label=f'RSI {period}', color='purple')
        plt.title(f'RSI {period}')
        plt.ylabel('RSI')
        plt.legend()

    # Форматирование дат на оси X
    date_form = DateFormatter("%m-%d %H:%M")
    plt.gca().xaxis.set_major_formatter(date_form)

    plt.tight_layout()
    plt.show()

# Параметры для загрузки данных
symbol = "BTCUSDT"
interval = Client.KLINE_INTERVAL_1MINUTE
start_time = "1 day ago UTC"
end_time = "now UTC"

# Загрузка данных
k_lines_data = fetch_binance_data(symbol, interval, start_time, end_time)

# Создание DataFrame из загруженных данных
k_lines_df = pd.DataFrame(k_lines_data, columns=['time', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])
k_lines_df['time'] = pd.to_datetime(k_lines_df['time'], unit='ms')
k_lines_df[['close', 'high', 'low', 'open']] = k_lines_df[['close', 'high', 'low', 'open']].astype(float)

# Расчет индикаторов
periods = [14, 27, 100]
k_lines_df = calculate_rsi(k_lines_df, periods)

# Визуализация
visualize_data(k_lines_df, periods)
