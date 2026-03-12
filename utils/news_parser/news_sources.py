#!/usr/bin/env python3
"""
News sources configuration
"""

from dataclasses import dataclass
from typing import List, Dict, Optional
from enum import Enum


class NewsCategory(Enum):
    """News categories"""
    POLITICS = "politics"
    ECONOMY = "economy"
    TECHNOLOGY = "technology"
    SPORTS = "sports"
    ENTERTAINMENT = "entertainment"
    HEALTH = "health"
    WORLD = "world"


@dataclass
class NewsSource:
    """News source configuration"""
    name: str
    url: str
    language: str
    category: NewsCategory
    rss_url: Optional[str] = None
    api_url: Optional[str] = None
    country: Optional[str] = None
    active: bool = True
    priority: int = 5  # 1-10, higher = more important


class NewsSources:
    """Collection of news sources"""
    
    def __init__(self):
        self.sources = self._load_sources()
    
    def _load_sources(self) -> List[NewsSource]:
        """Load all news sources"""
        return [
            # Kazakhstan
            NewsSource(
                name="Kazinform",
                url="https://www.inform.kz",
                rss_url="https://www.inform.kz/rss",
                language="kz",
                category=NewsCategory.POLITICS,
                country="KZ",
                priority=9
            ),
            NewsSource(
                name="Tengrinews",
                url="https://tengrinews.kz",
                rss_url="https://tengrinews.kz/rss",
                language="ru",
                category=NewsCategory.POLITICS,
                country="KZ",
                priority=8
            ),
            
            # International
            NewsSource(
                name="BBC News",
                url="https://www.bbc.com/news",
                rss_url="https://feeds.bbci.co.uk/news/rss.xml",
                language="en",
                category=NewsCategory.WORLD,
                country="UK",
                priority=10
            ),
            NewsSource(
                name="Reuters",
                url="https://www.reuters.com",
                rss_url="https://www.reutersagency.com/feed/",
                language="en",
                category=NewsCategory.ECONOMY,
                country="US",
                priority=9
            ),
            
            # Technology
            NewsSource(
                name="TechCrunch",
                url="https://techcrunch.com",
                rss_url="https://techcrunch.com/feed/",
                language="en",
                category=NewsCategory.TECHNOLOGY,
                country="US",
                priority=8
            ),
            
            # Economy/Finance
            NewsSource(
                name="Bloomberg",
                url="https://www.bloomberg.com",
                api_url="https://www.bloomberg.com/markets2/api",
                language="en",
                category=NewsCategory.ECONOMY,
                country="US",
                priority=9
            ),
            
            # Russia
            NewsSource(
                name="RIA Novosti",
                url="https://ria.ru",
                rss_url="https://ria.ru/export/rss2/index.xml",
                language="ru",
                category=NewsCategory.POLITICS,
                country="RU",
                priority=7
            ),
        ]
    
    def get_by_category(self, category: NewsCategory) -> List[NewsSource]:
        """Get sources by category"""
        return [s for s in self.sources if s.category == category and s.active]
    
    def get_by_country(self, country: str) -> List[NewsSource]:
        """Get sources by country"""
        return [s for s in self.sources if s.country == country and s.active]
    
    def get_all_active(self) -> List[NewsSource]:
        """Get all active sources"""
        return [s for s in self.sources if s.active]
    
    def get_priority_sources(self, min_priority: int = 7) -> List[NewsSource]:
        """Get high priority sources"""
        return [s for s in self.sources if s.priority >= min_priority and s.active]