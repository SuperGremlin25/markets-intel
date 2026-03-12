"""
Local News Monitor - RSS feed aggregation for OK/TX local news
Monitors local news sources for crime, power, cyber, and emergency keywords
"""

from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError
import feedparser
from datetime import datetime, timedelta
import requests
import time
import re
from html import unescape


class LocalNewsMonitor:
    """
    Monitor local news RSS feeds for OK and TX
    """
    
    def __init__(self):
        self.feeds = {
            'oklahoma': {
                'okc_crime': {
                    'name': 'Oklahoma City Crime News',
                    'url': 'https://news.google.com/rss/search?q=%22Oklahoma%20City%22%20(crime%20OR%20shooting%20OR%20shot%20OR%20arrest%20OR%20police%20OR%20killed%20OR%20murder)%20when:2d&hl=en-US&gl=US&ceid=US:en',
                    'city': 'Oklahoma City'
                },
                'okc_breaking': {
                    'name': 'OKC Breaking News',
                    'url': 'https://news.google.com/rss/search?q=%22Oklahoma%20City%22%20(breaking%20OR%20incident%20OR%20investigation)%20when:2d&hl=en-US&gl=US&ceid=US:en',
                    'city': 'Oklahoma City'
                },
                'okc_weather': {
                    'name': 'Oklahoma City Weather',
                    'url': 'https://news.google.com/rss/search?q=Oklahoma%20City%20storm%20OR%20tornado%20OR%20weather%20OR%20flood%20when:3d&hl=en-US&gl=US&ceid=US:en',
                    'city': 'Oklahoma City'
                },
                'okc_power': {
                    'name': 'Oklahoma City Power',
                    'url': 'https://news.google.com/rss/search?q=Oklahoma%20City%20power%20OR%20outage%20OR%20OGE%20when:3d&hl=en-US&gl=US&ceid=US:en',
                    'city': 'Oklahoma City'
                },
                'oklahoman': {
                    'name': 'The Oklahoman',
                    'url': 'https://www.oklahoman.com/rss',
                    'city': 'Oklahoma City'
                },
                'tulsa_crime': {
                    'name': 'Tulsa Crime News',
                    'url': 'https://news.google.com/rss/search?q=Tulsa%20crime%20OR%20shooting%20OR%20arrest%20OR%20police%20when:3d&hl=en-US&gl=US&ceid=US:en',
                    'city': 'Tulsa'
                },
                'tulsa_weather': {
                    'name': 'Tulsa Weather',
                    'url': 'https://news.google.com/rss/search?q=Tulsa%20storm%20OR%20tornado%20OR%20weather%20OR%20flood%20when:3d&hl=en-US&gl=US&ceid=US:en',
                    'city': 'Tulsa'
                },
                'oklahoma_statewide': {
                    'name': 'Oklahoma Statewide',
                    'url': 'https://news.google.com/rss/search?q=Oklahoma%20emergency%20OR%20alert%20OR%20cyber%20when:3d&hl=en-US&gl=US&ceid=US:en',
                    'city': 'Oklahoma City'
                }
            },
        }
        
        self.keywords = {
            'power': ['power', 'outage', 'blackout', 'grid', 'electricity', 'utility', 'oge', 'pso'],
            'crime': ['crime', 'shooting', 'shot', 'fired', 'gunfire', 'robbery', 'assault', 'murder', 'killed', 'death', 'arrest', 'arrested', 'police', 'officer', 'suspect', 'investigation', 'homicide', 'burglary', 'theft', 'stolen', 'wanted', 'fugitive', 'jail', 'prison', 'convicted', 'charges', 'charged', 'indicted', 'victim', 'stabbing', 'stabbed', 'attack', 'attacked', 'violence', 'violent', 'weapon', 'gun', 'knife'],
            'cyber': ['cyber', 'hack', 'hacked', 'breach', 'breached', 'ransomware', 'data leak', 'security', 'scam', 'fraud'],
            'emergency': ['emergency', 'alert', 'warning', 'danger', 'evacuation', 'evacuate', 'rescue'],
            'weather': ['tornado', 'storm', 'flood', 'flooding', 'hurricane', 'severe weather', 'thunderstorm', 'hail', 'wind', 'rain', 'lightning']
        }
        
        self.last_request_time = 0
        self.min_request_interval = 1
        self.initial_feed_keys = {
            'oklahoma': ['okc_crime', 'okc_breaking', 'okc_weather', 'okc_power', 'oklahoman', 'tulsa_crime', 'tulsa_weather', 'oklahoma_statewide']
        }
    
    def _clean_html(self, text):
        """Remove HTML tags and decode entities from text"""
        if not text:
            return ''
        text = re.sub(r'<[^>]+>', '', text)
        text = unescape(text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def _rate_limit(self):
        """Ensure we don't make requests too quickly"""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.min_request_interval:
            time.sleep(self.min_request_interval - elapsed)
        self.last_request_time = time.time()
    
    def fetch_local_news(self, state, hours=24):
        """
        Fetch recent local news for a state
        """
        cutoff = datetime.now() - timedelta(hours=hours)
        articles = []
        
        state_feeds = self.feeds.get(state, {})
        
        for source_key, source_info in state_feeds.items():
            self._rate_limit()
            
            try:
                feed = feedparser.parse(source_info['url'])
                
                for entry in feed.entries:
                    try:
                        # Parse publication date
                        if hasattr(entry, 'published_parsed') and entry.published_parsed:
                            pub_date = datetime(*entry.published_parsed[:6])
                        else:
                            pub_date = datetime.now()
                        
                        # Only include recent articles
                        if pub_date >= cutoff:
                            # Check if article matches our keywords
                            title = entry.get('title', '')
                            summary = entry.get('summary', entry.get('description', ''))
                            text = (title + ' ' + summary).lower()
                            
                            # Categorize article
                            categories = self._categorize_article(text)
                            
                            if categories:  # Only include if it matches keywords
                                articles.append({
                                    'title': title,
                                    'summary': summary[:200] + '...' if len(summary) > 200 else summary,
                                    'link': entry.get('link', ''),
                                    'published': pub_date.isoformat(),
                                    'source': source_info['name'],
                                    'city': source_info['city'],
                                    'state': state.title(),
                                    'categories': categories
                                })
                    except Exception as e:
                        continue
                
            except Exception as e:
                print(f"Error fetching {source_info['name']}: {str(e)}")
                continue
        
        # Sort by date (newest first)
        articles.sort(key=lambda x: x['published'], reverse=True)
        
        return articles

    def fetch_single_feed(self, state, source_key, source_info, hours=24):
        cutoff = datetime.now() - timedelta(hours=hours)
        started = time.time()

        try:
            response = requests.get(source_info['url'], timeout=5, headers={'User-Agent': 'Mozilla/5.0'})
            response.raise_for_status()
            feed = feedparser.parse(response.content)

            articles = []
            for entry in feed.entries[:20]:
                try:
                    if hasattr(entry, 'published_parsed') and entry.published_parsed:
                        pub_date = datetime(*entry.published_parsed[:6])
                    else:
                        pub_date = datetime.now()

                    if pub_date < cutoff:
                        continue

                    title = self._clean_html(entry.get('title', ''))
                    summary = self._clean_html(entry.get('summary', entry.get('description', '')))
                    text = (title + ' ' + summary).lower()
                    categories = self._categorize_article(text)

                    if categories:
                        clean_summary = summary[:200] + '...' if len(summary) > 200 else summary
                        articles.append({
                            'title': title,
                            'summary': clean_summary,
                            'link': entry.get('link', ''),
                            'published': pub_date.isoformat(),
                            'source': source_info['name'],
                            'city': source_info['city'],
                            'state': state.title(),
                            'categories': categories
                        })
                except Exception:
                    continue

            return {
                'source_key': source_key,
                'source_name': source_info['name'],
                'articles': articles,
                'ok': True,
                'error': None,
                'duration_ms': int((time.time() - started) * 1000)
            }
        except Exception as e:
            return {
                'source_key': source_key,
                'source_name': source_info['name'],
                'articles': [],
                'ok': False,
                'error': str(e),
                'duration_ms': int((time.time() - started) * 1000)
            }

    def get_all_news_parallel(self, hours=24):
        feed_jobs = []
        for state, source_keys in self.initial_feed_keys.items():
            state_sources = self.feeds.get(state, {})
            for source_key in source_keys:
                if source_key in state_sources:
                    feed_jobs.append((state, source_key, state_sources[source_key]))

        results = []
        with ThreadPoolExecutor(max_workers=len(feed_jobs) or 1) as executor:
            futures = {
                executor.submit(self.fetch_single_feed, state, source_key, source_info, hours): source_key
                for state, source_key, source_info in feed_jobs
            }

            try:
                for future in as_completed(futures, timeout=8):
                    results.append(future.result())
            except TimeoutError:
                pass

        completed_keys = {result['source_key'] for result in results}
        for state, source_key, source_info in feed_jobs:
            if source_key not in completed_keys:
                results.append({
                    'source_key': source_key,
                    'source_name': source_info['name'],
                    'articles': [],
                    'ok': False,
                    'error': 'Global timeout',
                    'duration_ms': 8000
                })

        successful = [result for result in results if result['ok']]
        failed = [result for result in results if not result['ok']]

        all_articles = []
        for result in successful:
            all_articles.extend(result['articles'])

        all_articles.sort(key=lambda x: x['published'], reverse=True)

        categorized = {
            'power': [],
            'crime': [],
            'cyber': [],
            'emergency': [],
            'weather': []
        }

        for article in all_articles:
            for category in article['categories']:
                categorized[category].append(article)

        return {
            'all_articles': all_articles,
            'by_category': categorized,
            'successful_feeds': successful,
            'failed_feeds': failed,
            'total_count': len(all_articles),
            'successful_count': len(successful),
            'failed_count': len(failed),
            'timestamp': datetime.now().isoformat()
        }
    
    def _categorize_article(self, text):
        """
        Categorize article by matching keywords
        Returns list of matching categories
        """
        categories = []
        
        for category, keywords in self.keywords.items():
            if any(keyword in text for keyword in keywords):
                categories.append(category)
        
        return categories
    
    def get_all_news(self, hours=24):
        """
        Get news from all states
        """
        ok_news = self.fetch_local_news('oklahoma', hours)
        tx_news = self.fetch_local_news('texas', hours)
        
        all_news = ok_news + tx_news
        
        # Categorize by type
        categorized = {
            'power': [],
            'crime': [],
            'cyber': [],
            'emergency': [],
            'weather': []
        }
        
        for article in all_news:
            for category in article['categories']:
                categorized[category].append(article)
        
        return {
            'all_articles': all_news,
            'by_category': categorized,
            'total_count': len(all_news),
            'oklahoma_count': len(ok_news),
            'texas_count': len(tx_news),
            'timestamp': datetime.now().isoformat()
        }
    
    def get_breaking_news(self, hours=6):
        """
        Get very recent news (breaking)
        """
        news = self.get_all_news(hours)
        
        # Filter for emergency and high-priority categories
        breaking = []
        
        for article in news['all_articles']:
            # Consider it breaking if it's emergency or has multiple categories
            if 'emergency' in article['categories'] or len(article['categories']) >= 2:
                breaking.append(article)
        
        return breaking
    
    def get_summary_by_city(self, hours=24):
        """
        Get news summary grouped by city
        """
        all_news = self.get_all_news(hours)
        
        by_city = {}
        
        for article in all_news['all_articles']:
            city = article['city']
            if city not in by_city:
                by_city[city] = []
            by_city[city].append(article)
        
        # Sort cities by article count
        city_summaries = []
        for city, articles in by_city.items():
            city_summaries.append({
                'city': city,
                'article_count': len(articles),
                'articles': articles[:5],  # Top 5 per city
                'categories': self._get_city_categories(articles)
            })
        
        city_summaries.sort(key=lambda x: x['article_count'], reverse=True)
        
        return city_summaries
    
    def _get_city_categories(self, articles):
        """
        Get category breakdown for a city
        """
        categories = {}
        
        for article in articles:
            for cat in article['categories']:
                categories[cat] = categories.get(cat, 0) + 1
        
        return categories


# Example usage
if __name__ == "__main__":
    monitor = LocalNewsMonitor()
    
    print("Fetching local news from Oklahoma and Texas...")
    print("This may take a minute...\n")
    
    news = monitor.get_all_news(hours=24)
    
    print(f"=== LOCAL NEWS SUMMARY (Last 24 Hours) ===")
    print(f"Total Articles: {news['total_count']}")
    print(f"Oklahoma: {news['oklahoma_count']} articles")
    print(f"Texas: {news['texas_count']} articles")
    
    print(f"\n=== BY CATEGORY ===")
    for category, articles in news['by_category'].items():
        if articles:
            print(f"\n{category.upper()} ({len(articles)} articles):")
            for article in articles[:3]:  # Show top 3 per category
                print(f"  - {article['title']}")
                print(f"    {article['source']} | {article['city']}")
    
    print(f"\n=== BREAKING NEWS (Last 6 Hours) ===")
    breaking = monitor.get_breaking_news(hours=6)
    
    if breaking:
        for article in breaking[:5]:
            print(f"\n{article['title']}")
            print(f"Source: {article['source']} ({article['city']})")
            print(f"Categories: {', '.join(article['categories'])}")
    else:
        print("No breaking news detected")
    
    print(f"\n=== BY CITY ===")
    city_summaries = monitor.get_summary_by_city(hours=24)
    
    for city_summary in city_summaries[:5]:  # Top 5 cities
        print(f"\n{city_summary['city']}: {city_summary['article_count']} articles")
        for cat, count in city_summary['categories'].items():
            print(f"  {cat}: {count}")
