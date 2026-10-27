"""Financial arithmetic and classification. No model may override these values."""
import re
from datetime import datetime, timedelta, timezone
from urllib.parse import quote

CATEGORIES = {
    'results': ('CRITICAL', 95), 'M&A': ('CRITICAL', 92),
    'management_change': ('CRITICAL', 90), 'litigation': ('HIGH', 85),
    'fund_raise': ('HIGH', 82), 'capex': ('HIGH', 80), 'pledging': ('HIGH', 78),
    'credit_rating': ('MEDIUM', 72), 'insider_trading': ('MEDIUM', 70),
    'earnings_call': ('MEDIUM', 68), 'press_release': ('MEDIUM', 65),
    'dividend': ('MEDIUM', 60), 'bonus_split': ('MEDIUM', 58),
    'investor_meetings': ('LOW_NOISE', 35), 'postal_ballot': ('LOW_NOISE', 25),
    'agm_egm': ('LOW_NOISE', 25), 'unclassified': ('LOW_NOISE', 10),
}
DEFAULT_CATEGORIES = ['results','M&A','management_change','litigation','capex','pledging','fund_raise']
ALIASES = {'ZOMATO': 'ETERNAL', 'NARAYANA': 'NH'}

def resolve_symbol(value):
    value = value.strip().upper()
    exchange = 'BSE' if value.endswith('.BO') or value.startswith('BSE:') else 'NSE'
    value = re.sub(r'^(NSE|BSE):', '', value)
    value = re.sub(r'\.(NS|BO)$', '', value)
    if not re.fullmatch(r'[A-Z0-9][A-Z0-9&-]{0,29}', value):
        raise ValueError('Enter an NSE symbol or a numeric BSE scrip code, e.g. POLYCAB or 500325.BO.')
    if exchange == 'BSE' and not re.fullmatch(r'\d{6}', value):
        raise ValueError('Use the six-digit BSE scrip code with .BO, e.g. 500325.BO.')
    canonical = ALIASES.get(value, value)
    return {'symbol': canonical, 'requested_symbol': value, 'exchange': exchange,
            'yahoo': canonical + ('.BO' if exchange == 'BSE' else '.NS'),
            'screener': f'https://www.screener.in/company/{quote(canonical, safe="")}/consolidated/'}

def pct(current, previous):
    # A nonpositive base makes the usual growth percentage misleading.
    return None if current is None or previous is None or previous <= 0 else (current / previous - 1) * 100

def ratio(a, b):
    return None if a is None or b is None or b <= 0 else a / b

def bps(current, previous):
    return None if current is None or previous is None else (current - previous) * 100

def cagr(first, last, years):
    return None if not years or years <= 0 or first is None or last is None or first <= 0 or last <= 0 else ((last/first)**(1/years)-1)*100

def eod_metrics(bars, price_threshold=3., volume_threshold=2.):
    if len(bars) < 2:
        return {'status': 'insufficient_history', 'triggered': False}
    current, previous = bars[-1], bars[-2]
    change = pct(current['close'], previous['close'])
    baseline = bars[-21:-1]
    avg = sum(b['volume'] for b in baseline)/20 if len(baseline) == 20 else None
    rvol = ratio(current['volume'], avg)
    return {'status': 'ok' if avg is not None else 'insufficient_volume_history',
            'close': current['close'], 'date': current['date'], 'change_pct': change,
            'adv20': avg, 'rvol': rvol, 'volume': current['volume'],
            'triggered': (change is not None and abs(change) >= price_threshold) or (rvol is not None and rvol >= volume_threshold)}

def classify(text):
    text = text.lower()
    # Material warnings take precedence over routine auditor/compliance vocabulary.
    rules = [
        ('litigation', r'qualified opinion|adverse opinion|disclaimer of opinion|auditor.{0,40}resign|tax demand|penalt|insolvency|litigation|sebi order|rbi.{0,25}restriction'),
        ('management_change', r'change in (?:management|managing director|chief executive|chief financial)|\b(cfo|ceo|managing director|chief executive|chief financial)\b.{0,80}(appoint|resign|retir)|(?:appoint|resign).{0,80}\b(director|cfo|ceo)\b'),
        ('unclassified', r'trading window|74\s*\(?5|share certificate|newspaper|\besop\b|\besps\b'),
        ('earnings_call', r'earnings.{0,20}call|conference call|concall|transcript'),
        ('results', r'financial results|quarterly results|audited.{0,25}results|unaudited.{0,25}results'),
        ('M&A', r'acquisition|merger|demerger|joint venture|stake sale|disinvestment'),
        ('fund_raise', r'fund rais|qip|rights issue|preferential allot|buyback|commercial paper'),
        ('capex', r'capacity expansion|capital expenditure|new plant|commissioning'),
        ('pledging', r'pledg|encumbrance'),
        ('credit_rating', r'credit rating|rating.{0,20}(upgrade|downgrade|reaffirm)'),
        ('insider_trading', r'insider|promoter.{0,30}(purchase|sale|sell|buy)'),
        ('dividend', r'dividend'), ('bonus_split', r'bonus|stock split|sub.division'),
        ('investor_meetings', r'investor meet|analyst.{0,20}meet'),
        ('postal_ballot', r'postal ballot'), ('agm_egm', r'annual general|extraordinary general|\bagm\b|\begm\b'),
        ('press_release', r'order win|order.{0,20}award|bagging/receiving of orders|press release|product launch|partnership|investor presentation'),
    ]
    matched = next((c for c, p in rules if re.search(p, text)), None)
    category = matched or 'unclassified'
    tier, score = CATEGORIES[category]
    reason = 'Matched deterministic disclosure rules'
    if matched is None:
        tier,score,reason='MEDIUM',50,'Uncertain classification — needs review; not buried as routine'
    if category == 'results' and re.search(r'board meeting.{0,30}(intimation|scheduled)|intimation.{0,35}meeting', text):
        tier, score, reason = 'LOW_NOISE', 30, 'Meeting notice, not delivered results'
    if category == 'earnings_call' and not re.search(r'transcript|recording|audio|outcome', text):
        tier, score, reason = 'LOW_NOISE', 30, 'Call invitation, not new management commentary'
    return {'category': category, 'tier': tier, 'score': score, 'reason': reason, 'route': 'T0'}

def match_filing(symbol, close_at, filings):
    at = datetime.fromisoformat(close_at)
    candidates = [f for f in filings if f['symbol'] == symbol and f['tier'] != 'LOW_NOISE'
                  and at-timedelta(hours=48) <= datetime.fromisoformat(f['published_at']) <= at]
    return max(candidates, key=lambda f: f['score'], default=None)

def audit_guidance(item):
    """Comparable numeric, same-basis guidance only; maturity checked by caller."""
    actual, low, high = item.get('actual'), item.get('low'), item.get('high')
    if item.get('period_match') is not True or item.get('basis_match') is not True:
        return {'status': 'NOT_COMPARABLE', 'delta': None}
    if actual is None or low is None or high is None:
        return {'status': 'NOT_EVALUABLE', 'delta': None}
    direction = item.get('direction', 'higher')
    status = 'INLINE'
    if actual > high: status = 'BEAT' if direction == 'higher' else 'MISSED'
    if actual < low: status = 'MISSED' if direction == 'higher' else 'BEAT'
    delta = actual-high if actual > high else actual-low if actual < low else 0
    return {'status': status, 'delta': delta}

def credibility(rows):
    comparable = [x for x in rows if x['status'] in {'BEAT','INLINE','MISSED'}]
    return {'score': round(100*sum(x['status'] != 'MISSED' for x in comparable)/len(comparable)) if comparable else None,
            'sample_size': len(comparable), 'total': len(rows),
            'definition': 'Share of comparable, matured numeric commitments met or exceeded; not a personality score.'}

def cash_quality(cfo, ebitda):
    value = ratio(cfo, ebitda)
    return {'ratio': value, 'badge': 'UNKNOWN' if value is None else 'GREEN' if value > .8 else 'AMBER' if value >= .6 else 'RED',
            'review_flag': value is not None and value < .7}
