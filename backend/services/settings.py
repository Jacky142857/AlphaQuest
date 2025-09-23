from django.core.cache import cache

SETTINGS_KEY = "api:strategy_settings"
DEFAULTS = {
    'neutralization': 'Subindustry',
    'decay': 4,
    'truncation': 0.08,
    'pasteurization': 'On',
    'nanHandling': 'Off',
    'maxTrade': 'Off',
    'delay': 1,
    'commission': 0.001,
    'bookSize': 1000000,
    'minWeight': 0.01,
    'maxWeight': 0.05,
    'rebalanceFreq': 'Daily'
}

def get_settings():
    s = cache.get(SETTINGS_KEY)
    if s is None:
        cache.set(SETTINGS_KEY, DEFAULTS.copy(), None)
        return DEFAULTS.copy()
    return s

def update_settings(payload: dict):
    s = get_settings()
    s.update({k:v for k,v in payload.items() if k in s})
    cache.set(SETTINGS_KEY, s, None)
    return s
