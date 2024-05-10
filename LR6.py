import pandas as pd
import ta
from binance import Client
from dataclasses import dataclass
from typing import List

@dataclass
class Signal:
    time: pd.Timestamp
    asset: str
    quantity: float
    side: str
    entry: float
    take_profit: float
    stop_loss: float
    result: float = None
    closed_by: str = None

def perform_backtesting(k_lines: pd.DataFrame):
    signals = create_signals(k_lines)
    results = []
    for signal in signals:
        start_index = k_lines[k_lines['time'] == signal.time].index[0]
        data_slice = k_lines.iloc[start_index:]

        for _, row in data_slice.iterrows():
            if (signal.side == "sell" and row["low"] <= signal.take_profit) or (signal.side == "buy" and row["high"] >= signal.take_profit):
                signal.result = (signal.take_profit - signal.entry if signal.side == 'buy' else signal.entry - signal.take_profit)
                signal.closed_by = "TP"
            elif (signal.side == "sell" and row["high"] >= signal.stop_loss) or (signal.side == "buy" and row["low"] <= signal.stop_loss):
                signal.result = (signal.stop_loss - signal.entry if signal.side == 'buy' else signal.entry - signal.stop_loss)
                signal.closed_by = "SL"

            if signal.result is not None:
                results.append(signal)
                break
    return results

def calculate_statistics(trade_list: List[Signal]):
    total_pnl = sum(trade.result for trade in trade_list)
    total_profit = sum(trade.result for trade in trade_list if trade.result > 0)
    total_loss = sum(trade.result for trade in trade_list if trade.result < 0)
    print(f"Total P&L: {total_pnl}")
    print(f"Profit Factor: {total_profit / abs(total_loss) if total_loss != 0 else 'undefined'}")

def create_signals(k_lines):
    signals = []
    for index, row in k_lines.iterrows():
        current_price = row['close']
        if row['cci'] < -100 and row['adx'] > 25:
            side = 'sell'
            stop_loss_price = round((1 + 0.01) * current_price, 1)
            take_profit_price = round((1 - 0.015) * current_price, 1)
        elif row['cci'] > 100 and row['adx'] > 25:
            side = 'buy'
            stop_loss_price = round((1 - 0.01) * current_price, 1)
            take_profit_price = round((1 + 0.015) * current_price, 1)
        else:
            continue

        signals.append(Signal(time=row['time'], asset='BTCUSDT', quantity=100, side=side, entry=current_price, take_profit=take_profit_price, stop_loss=stop_loss_price))
    return signals

client = Client()
k_lines = client.get_historical_klines(
    symbol="BTCUSDT",
    interval=Client.KLINE_INTERVAL_1MINUTE,
    start_str="1 week ago UTC",
    end_str="now UTC"
)

k_lines = pd.DataFrame(k_lines, columns=['time', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])
k_lines['time'] = pd.to_datetime(k_lines['time'], unit='ms')
k_lines['close'] = k_lines['close'].astype(float)
k_lines['high'] = k_lines['high'].astype(float)
k_lines['low'] = k_lines['low'].astype(float)
k_lines['open'] = k_lines['open'].astype(float)

k_lines['adx'] = ta.trend.ADXIndicator(k_lines['high'], k_lines['low'], k_lines['close']).adx()
k_lines['cci'] = ta.trend.CCIIndicator(k_lines['high'], k_lines['low'], k_lines['close']).cci()

results = perform_backtesting(k_lines)
for result in results:
    print(f"Time: {result.time}, Asset: {result.asset}, Quantity: {result.quantity}, Side: {result.side}, Entry: {result.entry}, Take Profit: {result.take_profit}, Stop Loss: {result.stop_loss}, Result: {result.result}, Closed_by: {result.closed_by}")
calculate_statistics(results)
