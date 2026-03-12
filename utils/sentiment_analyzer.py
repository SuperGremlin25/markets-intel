from concurrent.futures import ThreadPoolExecutor
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

_vader = SentimentIntensityAnalyzer()


def score_article(article: dict) -> dict:
    text = f"{article.get('title', '')}. {article.get('summary', '')}"
    scores = _vader.polarity_scores(text)
    compound = scores['compound']

    if compound >= 0.05:
        label = '🟢 Positive'
    elif compound <= -0.05:
        label = '🔴 Negative'
    else:
        label = '⚪ Neutral'

    return {
        **article,
        'sentiment_score': compound,
        'sentiment_label': label,
        'sentiment_pos': scores['pos'],
        'sentiment_neg': scores['neg'],
        'sentiment_neu': scores['neu'],
    }


def score_articles_parallel(articles: list) -> list:
    if not articles:
        return []

    max_workers = min(8, max(1, len(articles)))
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        return list(executor.map(score_article, articles))
