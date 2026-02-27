from sklearn.linear_model import LinearRegression
import yfinance as yf
import pandas as pd
import numpy as np
from typing import Tuple, List


def train_linear_model(symbol: str, period: str = "1mo") -> Tuple[LinearRegression, int]:
    """Return a trained model plus the number of samples used (time index length)."""
    data = yf.download(symbol, period=period)
    if data.empty:
        raise ValueError("No data for symbol")
    data = data.reset_index()
    data['t'] = range(len(data))
    X = data[['t']].values
    y = data['Close'].values
    model = LinearRegression()
    model.fit(X, y)
    return model, len(data)


def predict_price(model: LinearRegression, base_index: int, minutes_ahead: int) -> float:
    """Predict price minutes ahead given the base index of training data."""
    t_future = base_index + minutes_ahead
    return float(model.intercept_ + model.coef_[0] * t_future)


# Autoregressive daily model for multi-day forecasts
def train_ar_model(symbol: str, period: str = "6mo", lags: int = 5) -> Tuple[LinearRegression, List[float]]:
    """Train a linear autoregressive model using previous `lags` daily closes.

    Returns the trained model and the last `lags` values as the seed window.
    """
    data = yf.download(symbol, period=period, interval='1d')
    if data.empty:
        raise ValueError("No daily data for symbol")
    series = data['Close'].dropna().values
    if len(series) <= lags:
        raise ValueError("Not enough data for AR training")

    X, y = [], []
    for i in range(lags, len(series)):
        X.append(series[i - lags:i])
        y.append(series[i])

    X = np.array(X)
    y = np.array(y)
    model = LinearRegression()
    model.fit(X, y)

    last_window = list(series[-lags:])
    return model, last_window


def predict_days(model: LinearRegression, last_window: List[float], days_ahead: int) -> List[float]:
    """Iteratively predict `days_ahead` future daily prices using the AR model.

    Returns the list of predicted prices (length = days_ahead).
    """
    if days_ahead <= 0:
        return []
    lags = len(last_window)
    window = list(last_window)
    preds: List[float] = []
    for _ in range(days_ahead):
        x = np.array(window[-lags:]).reshape(1, -1)
        next_p = float(model.predict(x)[0])
        preds.append(next_p)
        window.append(next_p)
    return preds
