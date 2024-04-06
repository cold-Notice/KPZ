import pandas as pd
import ta
from matplotlib import pyplot as plt
from binance.client import Client
from dataclasses import dataclass

# Определение класса для хранения информации о сигналах
@dataclass
class Signal:
    time: pd.Timestamp
    asset: str
    quantity: float
    side: str
    entry: float
    take_profit: float
    stop_loss: float
    result: float

# Функция для генерации сигналов купли/продажи
def create_signals(k_lines):
    signals = []
    for i in range(len(k_lines)):
        signal = None
        current_price = k_lines.iloc[i]['close']
        cci = k_lines.iloc[i]['cci']
        adx = k_lines.iloc[i]['adx']
        
        # Логика для определения сигналов на основе CCI и ADX
        if cci < -100 and adx > 25:
            signal = 'sell'
        elif cci > 100 and adx > 25:
            signal = 'buy'

        # Расчет цен Take Profit и Stop Loss
        if signal:
            stop_loss_price = round((1 - 0.02) * current_price, 1) if signal == "buy" else round((1 + 0.02) * current_price, 1)
            take_profit_price = round((1 + 0.1) * current_price, 1) if signal == "buy" else round((1 - 0.1) * current_price, 1)

            signals.append(Signal(
                k_lines.iloc[i]['time'],
                'BTCUSDT',
                100,
                signal,
                current_price,
                take_profit_price,
                stop_loss_price,
                None
            ))
    return signals

# Загрузка данных с Binance
client = Client()
k_lines = client.get_historical_klines(
    symbol="BTCUSDT",
    interval=Client.KLINE_INTERVAL_1MINUTE,
    start_str="1 week ago UTC",
    end_str="now UTC"
)

# Создание DataFrame из загруженных данных
k_lines = pd.DataFrame(k_lines,
                       columns=['time', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume',
                                'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume',
                                'ignore'])
k_lines['time'] = pd.to_datetime(k_lines['time'], unit='ms')
k_lines[['close', 'high', 'low', 'open']] = k_lines[['close', 'high', 'low', 'open']].astype(float)

# Расчет индикаторов ADX и CCI
k_lines['adx'] = ta.trend.ADXIndicator(k_lines['high'], k_lines['low'], k_lines['close']).adx()
k_lines['cci'] = ta.trend.CCIIndicator(k_lines['high'], k_lines['low'], k_lines['close']).cci()

# Генерация сигналов
signals = create_signals(k_lines)

# Визуализация данных и сигналов
plt.figure(figsize=(12, 6))
plt.plot(k_lines['time'], k_lines['close'], label='Цена BTCUSDT')

# Отображение сигналов на графике
for signal in signals:
    if signal.side:
        plt.scatter(signal.time, signal.entry, color='green' if signal.side == 'buy' else 'red', label=f'{signal.side.capitalize()} signal', marker='^' if signal.side == 'buy' else 'v', s=100)

plt.title('Цена BTCUSDT и сигналы')
plt.xlabel('Время')
plt.ylabel('Цена')
plt.legend()
plt.grid(True)
plt.show()
