import httpx

from app.core.config import settings


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
            return symbol.isalpha() and 1 <= len(symbol) <= 5
        data = resp.json()
        return bool(data.get("ticker")) or (symbol.isalpha() and 1 <= len(symbol) <= 5)
    except Exception:
        return symbol.isalpha() and 1 <= len(symbol) <= 5
