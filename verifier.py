import os
import re
import requests

FACTCHECK_URL = 'https://factchecktools.googleapis.com/v1alpha1/claims:search'
NEWS_URL = 'https://newsapi.org/v2/everything'
HEADLINES_URL = 'https://newsapi.org/v2/top-headlines'

SENSATIONAL = [
    r'\bshocking\b', r'\bunbelievable\b', r'\b100%\s*true\b',
    r'\bshare\s+(this|now|immediately)\b', r'\bsecret cure\b',
    r'\bguaranteed\b', r'\bviral\b', r'\bexposed\b', r"\byou won't believe\b"
]

SOURCE_HINTS = [
    'according to', 'reported by', 'official statement', 'press release',
    'ministry', 'police', 'court', 'university', 'study', 'report'
]


def normalize(text):
    return ' '.join(text.split())


def heuristic_checks(text):
    lowered = text.lower()
    red_flags = []
    positive = []

    for pattern in SENSATIONAL:
        if re.search(pattern, lowered, flags=re.I):
            red_flags.append('Sensational or emotionally loaded wording detected.')
            break

    if any(h in lowered for h in SOURCE_HINTS):
        positive.append('The claim contains source or attribution language.')
    if re.search(r'https?://', text):
        positive.append('A web link is included.')
    if re.search(r'\b(19|20)\d{2}\b', text):
        positive.append('A date/year reference is included.')
    if len(text.split()) < 12:
        red_flags.append('The claim is very short and lacks context.')

    score = 50 - min(len(red_flags)*10, 30) + min(len(positive)*5, 15)
    return max(0, min(100, score)), red_flags, positive


def fact_check_search(query):
    key = os.getenv('GOOGLE_FACTCHECK_API_KEY')
    if not key:
        return []
    r = requests.get(FACTCHECK_URL, params={
        'query': query[:500], 'key': key, 'languageCode': 'en', 'pageSize': 5
    }, timeout=12)
    r.raise_for_status()

    results = []
    for claim in r.json().get('claims', []):
        reviews = claim.get('claimReview', [])
        if not reviews:
            continue
        review = reviews[0]
        results.append({
            'claim': claim.get('text',''),
            'claimant': claim.get('claimant',''),
            'rating': review.get('textualRating','Unknown'),
            'publisher': (review.get('publisher') or {}).get('name',''),
            'url': review.get('url',''),
            'review_date': review.get('reviewDate','')
        })
    return results


def news_search(query):
    key = os.getenv('NEWSAPI_KEY')
    if not key:
        return []
    r = requests.get(NEWS_URL, params={
        'q': query[:180], 'language':'en', 'sortBy':'relevancy',
        'pageSize':5, 'apiKey':key
    }, timeout=12)
    r.raise_for_status()
    return [{
        'title': a.get('title',''),
        'source': (a.get('source') or {}).get('name',''),
        'url': a.get('url',''),
        'published_at': a.get('publishedAt',''),
        'description': a.get('description','')
    } for a in r.json().get('articles', [])]


def analyze_news_text(text):
    text = normalize(text)
    query = ' '.join(re.sub(r'https?://\S+','',text).split()[:28])
    score, red_flags, positive = heuristic_checks(text)
    notes = []

    try:
        facts = fact_check_search(query)
    except Exception as exc:
        facts = []
        notes.append(f'Fact-check lookup failed: {exc}')

    try:
        news = news_search(query)
    except Exception as exc:
        news = []
        notes.append(f'News lookup failed: {exc}')

    if facts:
        ratings = ' '.join(x['rating'].lower() for x in facts)
        if any(t in ratings for t in ['false','fake','misleading','incorrect']):
            verdict, confidence = 'Potentially false or misleading', 'High'
        elif any(t in ratings for t in ['true','correct','accurate']):
            verdict, confidence = 'Likely supported', 'High'
        else:
            verdict, confidence = 'Needs review', 'Medium'
    elif news:
        verdict, confidence = 'Related reporting found', 'Medium'
    else:
        verdict, confidence = 'Insufficient evidence', 'Low'

    return {
        'verdict': verdict,
        'confidence': confidence,
        'claim_text': text,
        'fact_checks': facts,
        'news_matches': news,
        'heuristic_score': score,
        'red_flags': red_flags,
        'positive_signals': positive,
        'service_notes': notes,
        'explanation': ('WorldLens does not decide truth from wording alone. It combines fact-check '
                        'matches, related reporting and basic language signals. Without API keys, '
                        'the result is only a preliminary assessment.')
    }


def fetch_latest_events(country='in', category='general'):
    key = os.getenv('NEWSAPI_KEY')
    if not key:
        raise RuntimeError('NEWSAPI_KEY is not configured. Add it to .env to load live headlines.')

    r = requests.get(HEADLINES_URL, params={
        'country':country, 'category':category, 'pageSize':12, 'apiKey':key
    }, timeout=12)
    r.raise_for_status()

    return [{
        'title': a.get('title',''),
        'source': (a.get('source') or {}).get('name',''),
        'description': a.get('description',''),
        'url': a.get('url',''),
        'published_at': a.get('publishedAt',''),
        'image': a.get('urlToImage','')
    } for a in r.json().get('articles', [])]
