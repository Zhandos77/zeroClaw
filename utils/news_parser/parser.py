#!/usr/bin/env python3
"""
News parser implementation
"""

import json
import time
from datetime import datetime
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, asdict
import feedparser
import requests
from bs4 import BeautifulSoup

from .news_sources import NewsSource, NewsCategory


@dataclass
class NewsItem:
    """News item data"""
    title: str
    url: str
    summary: Optional[str] = None
    published: Optional[str] = None
    source: Optional[str] = None
    category: Optional[str] = None
    language: Optional[str] = None
    country: Optional[str] = None
    image_url: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return asdict(self)
    
    def __str__(self) -> str:
        return f"{self.title} ({self.source})"


class NewsParser:
    """News parser class"""
    
    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; NewsParser/1.0)'
        })
    
    def parse_rss(self, rss_url: str, source: NewsSource) -> List[NewsItem]:
        """Parse RSS feed"""
        try:
            feed = feedparser.parse(rss_url)
            news_items = []
            
            for entry in feed.entries[:10]:  # Limit to 10 items
                item = NewsItem(
                    title=entry.get('title', 'No title'),
                    url=entry.get('link', ''),
                    summary=entry.get('summary', ''),
                    published=entry.get('published', ''),
                    source=source.name,
                    category=source.category.value,
                    language=source.language,
                    country=source.country,
                    image_url=self._extract_image(entry)
                )
                news_items.append(item)
            
            return news_items
            
        except Exception as e:
            print(f"Error parsing RSS {rss_url}: {e}")
            return []
    
    def parse_web(self, url: str, source: NewsSource) -> List[NewsItem]:
        """Parse web page (basic implementation)"""
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Basic extraction - would need customization per site
            news_items = []
            
            # Try to find article links
            for link in soup.find_all('a', href=True)[:10]:
                title = link.get_text(strip=True)
                href = link['href']
                
                if title and len(title) > 10 and href.startswith('http'):
                    # Make absolute URL if needed
                    if not href.startswith('http'):
                        href = source.url.rstrip('/') + '/' + href.lstrip('/')
                    
                    item = NewsItem(
                        title=title,
                        url=href,
                        source=source.name,
                        category=source.category.value,
                        language=source.language,
                        country=source.country
                    )
                    news_items.append(item)
            
            return news_items[:5]  # Limit to 5 items
            
        except Exception as e:
            print(f"Error parsing web {url}: {e}")
            return []
    
    def _extract_image(self, entry) -> Optional[str]:
        """Extract image URL from RSS entry"""
        # Try different image fields
        for field in ['media_content', 'media_thumbnail', 'links']:
            if field in entry:
                if isinstance(entry[field], list) and len(entry[field]) > 0:
                    item = entry[field][0]
                    if 'url' in item:
                        return item['url']
        
        # Check for enclosure
        if 'enclosures' in entry and entry.enclosures:
            for enc in entry.enclosures:
                if enc.get('type', '').startswith('image/'):
                    return enc.get('href')
        
        return None
    
    def fetch_news(self, sources: List[NewsSource], limit_per_source: int = 5) -> List[NewsItem]:
        """Fetch news from multiple sources"""
        all_news = []
        
        for source in sources:
            try:
                if source.rss_url:
                    items = self.parse_rss(source.rss_url, source)
                elif source.api_url:
                    # API parsing would go here
                    items = []
                else:
                    items = self.parse_web(source.url, source)
                
                # Limit items per source
                items = items[:limit_per_source]
                all_news.extend(items)
                
                # Be respectful to servers
                time.sleep(0.5)
                
            except Exception as e:
                print(f"Error fetching from {source.name}: {e}")
                continue
        
        # Sort by date if available
        try:
            all_news.sort(key=lambda x: x.published or "", reverse=True)
        except:
            pass
        
        return all_news
    
    def save_to_json(self, news_items: List[NewsItem], filename: str):
        """Save news to JSON file"""
        data = {
            'fetched_at': datetime.now().isoformat(),
            'total_items': len(news_items),
            'news': [item.to_dict() for item in news_items]
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def format_for_display(self, news_items: List[NewsItem], limit: int = 10) -> str:
        """Format news for display"""
        if not news_items:
            return "No news found."
        
        output = []
        output.append(f"📰 **Latest News** ({len(news_items)} items)\n")
        
        for i, item in enumerate(news_items[:limit], 1):
            source_info = f"{item.source}"
            if item.country:
                source_info += f" ({item.country})"
            
            output.append(f"{i}. **{item.title}**")
            output.append(f"   📍 {source_info}")
            if item.published:
                output.append(f"   📅 {item.published}")
            if item.summary and len(item.summary) < 200:
                output.append(f"   📝 {item.summary[:150]}...")
            output.append(f"   🔗 {item.url}")
            output.append("")
        
        return "\n".join(output)