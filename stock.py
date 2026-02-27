import threading
import time
from typing import Dict, List

import yfinance as yf
import pandas as pd

# Global store for alerts and a condition for notifying SSE listeners
alerts: List[Dict] = []
alert_condition = threading.Condition()


class StockMonitor:
    def __init__(self, symbol: str, threshold: float, interval: int = 60, on_alert=None):
        self.symbol = symbol
        self.threshold = threshold
        self.interval = interval  # seconds
        self.on_alert = on_alert
        self._stop = threading.Event()
        self.thread = threading.Thread(target=self._run)

    def start(self):
        self.thread.start()

    def stop(self):
        self._stop.set()
        self.thread.join()

    def _run(self):
        while not self._stop.is_set():
            price = self._get_price()
            if price is not None and price >= self.threshold:
                alert = {
                    "symbol": self.symbol,
                    "price": price,
                    "threshold": self.threshold,
                    "time": pd.Timestamp.now().isoformat(),
                }
                with alert_condition:
                    alerts.append(alert)
                    alert_condition.notify_all()
                # call callback if provided (for WebSocket emit)
                try:
                    if callable(self.on_alert):
                        self.on_alert(alert)
                except Exception:
                    pass
            time.sleep(self.interval)

    def _get_price(self) -> float:
        try:
            ticker = yf.Ticker(self.symbol)
            data = ticker.history(period="1d", interval="1m")
            if not data.empty:
                return float(data["Close"].iloc[-1])
        except Exception:
            pass
        return None
