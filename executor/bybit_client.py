import ccxt
from config import API_KEY, API_SECRET

def get_authenticated_client():
    return ccxt.bybit({
        'apiKey': API_KEY,
        'secret': API_SECRET,
        'enableRateLimit': True
    })
