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


def get_security_detail(ticker: str) -> dict | None:
    """Fetch enriched security metadata from EODHD search API.

    Returns a dict with name, exchanges, type, and previous close, or None
    if the ticker is not found, the API key is not configured, or the request fails.
    """
    if not settings.eodhd_api_key:
        return None

    symbol = ticker.strip().upper()
    if not symbol:
        return None

    try:
        with httpx.Client(timeout=10) as client:
            resp = client.get(
                f"{settings.eodhd_api_base_url}/search/{symbol}",
                params={"api_token": settings.eodhd_api_key, "fmt": "json", "limit": 50},
            )
        if resp.status_code != 200:
            logger.warning("EODHD search returned %d for %s", resp.status_code, symbol)
            return None

        results = resp.json()
        if not isinstance(results, list):
            return None

        exact_matches = [r for r in results if r.get("Code", "").upper() == symbol]
        if not exact_matches:
            return None

        primary = next((r for r in exact_matches if r.get("isPrimary")), exact_matches[0])
        exchanges = list(dict.fromkeys(r["Exchange"] for r in exact_matches if r.get("Exchange")))

        return {
            "ticker": symbol,
            "name": primary.get("Name", ""),
            "exchanges": exchanges,
            "type": primary.get("Type", ""),
            "previous_close": primary.get("previousClose"),
            "previous_close_date": primary.get("previousCloseDate"),
        }
    except Exception as exc:
        logger.warning("EODHD security detail fetch failed for %s: %s", symbol, exc)
        return None
