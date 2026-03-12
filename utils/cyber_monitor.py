"""
Cyber Threat Monitor - Track cyber threats and service outages
Monitors CISA alerts and Downdetector for cyber security intelligence
"""

import feedparser
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import time


class CyberThreatMonitor:
    """
    Monitor CISA alerts and Downdetector
    100% free sources
    """
    
    def __init__(self):
        self.cisa_feeds = [
            'https://www.cisa.gov/cybersecurity-advisories/all.xml',
            'https://www.us-cert.gov/ncas/alerts.xml',
            'https://www.us-cert.gov/ncas/current-activity.xml'
        ]
        
        self.critical_services = [
            'internet', 'att', 'verizon', 'tmobile', 'spectrum',
            'xfinity', 'cox', 'frontier', 'banking', 'paypal',
            'venmo', 'cashapp', 'gmail', 'outlook', 'microsoft',
            'google', 'amazon', 'facebook', 'twitter', 'instagram'
        ]
        
        self.last_request_time = 0
        self.min_request_interval = 2
    
    def _rate_limit(self):
        """Ensure we don't make requests too quickly"""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.min_request_interval:
            time.sleep(self.min_request_interval - elapsed)
        self.last_request_time = time.time()
    
    def _get_headers(self):
        """Headers for web requests"""
        return {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def fetch_cisa_alerts(self, days=7):
        """
        Fetch recent CISA alerts
        """
        all_alerts = []
        cutoff_date = datetime.now() - timedelta(days=days)
        
        for feed_url in self.cisa_feeds:
            try:
                self._rate_limit()
                
                feed = feedparser.parse(feed_url)
                
                for entry in feed.entries:
                    try:
                        # Parse publication date
                        if hasattr(entry, 'published_parsed') and entry.published_parsed:
                            pub_date = datetime(*entry.published_parsed[:6])
                        else:
                            pub_date = datetime.now()
                        
                        # Only include recent alerts
                        if pub_date >= cutoff_date:
                            all_alerts.append({
                                'title': entry.get('title', 'Unknown'),
                                'summary': entry.get('summary', ''),
                                'link': entry.get('link', ''),
                                'published': pub_date.isoformat(),
                                'severity': self._extract_severity(entry.get('title', '')),
                                'category': self._categorize_alert(
                                    entry.get('title', ''),
                                    entry.get('summary', '')
                                ),
                                'source': 'CISA'
                            })
                    except Exception as e:
                        continue
                
            except Exception as e:
                print(f"Error fetching CISA feed {feed_url}: {str(e)}")
                continue
        
        # Sort by date (newest first)
        all_alerts.sort(key=lambda x: x['published'], reverse=True)
        
        return all_alerts
    
    def _extract_severity(self, title):
        """
        Extract severity from alert title
        """
        title_lower = title.lower()
        
        if 'critical' in title_lower:
            return 'critical'
        elif 'high' in title_lower:
            return 'high'
        elif 'medium' in title_lower or 'moderate' in title_lower:
            return 'medium'
        elif 'low' in title_lower:
            return 'low'
        else:
            return 'medium'  # Default
    
    def _categorize_alert(self, title, summary):
        """
        Categorize alert by type
        """
        text = (title + ' ' + summary).lower()
        
        if any(word in text for word in ['ransomware', 'malware', 'virus', 'trojan']):
            return 'malware'
        elif any(word in text for word in ['phishing', 'social engineering', 'scam']):
            return 'phishing'
        elif any(word in text for word in ['vulnerability', 'exploit', 'cve', 'patch']):
            return 'vulnerability'
        elif any(word in text for word in ['ddos', 'denial of service', 'dos']):
            return 'ddos'
        elif any(word in text for word in ['breach', 'data leak', 'compromise']):
            return 'breach'
        else:
            return 'other'
    
    def calculate_threat_level(self, alerts):
        """
        Pure Python threat level calculation
        0-10 scale (0 = safe, 10 = critical)
        """
        if not alerts:
            return 2.0  # Baseline threat level
        
        severity_weights = {
            'critical': 1.0,
            'high': 0.7,
            'medium': 0.4,
            'low': 0.1
        }
        
        # Weight by recency (more recent = higher weight)
        now = datetime.now()
        weighted_score = 0
        total_weight = 0
        
        for alert in alerts:
            try:
                pub_date = datetime.fromisoformat(alert['published'])
                days_old = (now - pub_date).days
                
                # Decay over 7 days
                recency_weight = max(0.1, 1.0 - (days_old / 7))
                
                severity_score = severity_weights.get(alert['severity'], 0.4)
                weighted_score += severity_score * recency_weight
                total_weight += recency_weight
            except Exception:
                continue
        
        if total_weight == 0:
            return 2.0
        
        avg_score = weighted_score / total_weight
        
        # Scale to 0-10
        threat_level = min(10, avg_score * 10)
        
        return round(threat_level, 1)
    
    def scrape_downdetector(self, service):
        """
        Check if a service is experiencing outages on Downdetector
        """
        self._rate_limit()
        
        url = f"https://downdetector.com/status/{service}"
        
        try:
            response = requests.get(url, headers=self._get_headers(), timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Look for outage indicators
                # Downdetector uses specific classes for status
                status_text = soup.get_text().lower()
                
                # Simple heuristic - look for problem indicators
                has_problem = any(word in status_text for word in [
                    'problem', 'outage', 'down', 'issue', 'reports'
                ])
                
                if has_problem:
                    # Try to extract report count
                    # This is a simplified version
                    return {
                        'service': service,
                        'status': 'outage',
                        'timestamp': datetime.now().isoformat()
                    }
        
        except Exception as e:
            print(f"Error checking Downdetector for {service}: {str(e)}")
        
        return None
    
    def monitor_critical_services(self):
        """
        Monitor critical infrastructure services
        """
        outages = []
        
        # Only check a subset to avoid rate limiting
        # In production, you'd want to cache and rotate through services
        services_to_check = self.critical_services[:5]
        
        for service in services_to_check:
            outage = self.scrape_downdetector(service)
            if outage:
                outages.append(outage)
        
        return outages
    
    def get_cyber_intelligence_summary(self):
        """
        Get comprehensive cyber threat summary
        """
        # Fetch CISA alerts
        alerts = self.fetch_cisa_alerts(days=7)
        
        # Calculate threat level
        threat_level = self.calculate_threat_level(alerts)
        
        # Check for service outages
        service_outages = self.monitor_critical_services()
        
        # Categorize alerts
        alert_categories = {}
        for alert in alerts:
            category = alert['category']
            alert_categories[category] = alert_categories.get(category, 0) + 1
        
        # Determine status
        if threat_level >= 7:
            status = 'critical'
        elif threat_level >= 5:
            status = 'elevated'
        elif threat_level >= 3:
            status = 'moderate'
        else:
            status = 'low'
        
        return {
            'threat_level': threat_level,
            'status': status,
            'total_alerts': len(alerts),
            'recent_alerts': alerts[:10],  # Most recent 10
            'alert_categories': alert_categories,
            'service_outages': service_outages,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_alert_summary_text(self, summary):
        """
        Generate human-readable summary text
        Pure Python - no AI needed
        """
        threat_level = summary['threat_level']
        status = summary['status'].upper()
        total_alerts = summary['total_alerts']
        
        # Build summary
        lines = []
        lines.append(f"Cyber Threat Level: {threat_level}/10 ({status})")
        lines.append(f"Total Alerts (7 days): {total_alerts}")
        
        if summary['alert_categories']:
            lines.append("\nAlert Breakdown:")
            for category, count in summary['alert_categories'].items():
                lines.append(f"  {category.title()}: {count}")
        
        if summary['service_outages']:
            lines.append(f"\nService Outages Detected: {len(summary['service_outages'])}")
            for outage in summary['service_outages']:
                lines.append(f"  - {outage['service'].title()}")
        
        if summary['recent_alerts']:
            lines.append("\nMost Recent Alerts:")
            for alert in summary['recent_alerts'][:3]:
                lines.append(f"  - [{alert['severity'].upper()}] {alert['title']}")
        
        return '\n'.join(lines)


# Example usage
if __name__ == "__main__":
    monitor = CyberThreatMonitor()
    
    print("Fetching cyber threat intelligence...")
    print("This may take a minute...\n")
    
    summary = monitor.get_cyber_intelligence_summary()
    
    print("=== CYBER THREAT INTELLIGENCE ===")
    print(monitor.get_alert_summary_text(summary))
    
    print(f"\n=== DETAILED ALERTS ===")
    for alert in summary['recent_alerts'][:5]:
        print(f"\n[{alert['severity'].upper()}] {alert['title']}")
        print(f"Category: {alert['category']}")
        print(f"Published: {alert['published']}")
        print(f"Link: {alert['link']}")
