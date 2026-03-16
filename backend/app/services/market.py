import logging

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


def validate_ticker(ticker: str) -> bool:
    symbol = ticker.strip().upper()
    if not symbol:
        return False

    if not settings.market_api_key:
        return symbol.isalpha() and 1 <= len(symbol) <= 5

    try:
        with httpx.Client(timeout=10) as client:
            resp = client.get(
                f"{settings.market_api_base_url}/stock/profile2",
                params={"symbol": symbol, "token": settings.market_api_key},
            )
        if resp.status_code != 200:
            logger.warning("Finnhub /stock/profile2 returned %d for %s, falling back to regex validation", resp.status_code, symbol)
            return symbol.isalpha() and 1 <= len(symbol) <= 5
        data = resp.json()
        return bool(data.get("ticker")) or (symbol.isalpha() and 1 <= len(symbol) <= 5)
    except Exception as exc:
        logger.warning("Finnhub ticker validation error for %s: %s, falling back to regex", symbol, exc)
        return symbol.isalpha() and 1 <= len(symbol) <= 5


def get_price_snapshot(tickers: list[str]) -> dict[str, float]:
    """Fetch current prices for a list of tickers from Finnhub.

    Returns a dict mapping ticker -> last price. Skips tickers that fail.
    Returns an empty dict when market_api_key is not configured.
    """
    if not tickers or not settings.market_api_key:
        return {}

    prices: dict[str, float] = {}
    with httpx.Client(timeout=10) as client:
        for ticker in tickers[:15]:  # cap to avoid rate-limit bursts
            symbol = ticker.strip().upper()
            if not symbol:
                continue
            try:
                resp = client.get(
                    f"{settings.market_api_base_url}/quote",
                    params={"symbol": symbol, "token": settings.market_api_key},
                )
                if resp.status_code == 200:
                    data = resp.json()
                    current_price = data.get("c")  # "c" = current price in Finnhub
                    if current_price:
                        prices[symbol] = float(current_price)
                else:
                    logger.warning("Finnhub /quote returned %d for %s", resp.status_code, symbol)
            except Exception as exc:
                logger.warning("Price fetch failed for %s: %s", symbol, exc)
                continue

    return prices
