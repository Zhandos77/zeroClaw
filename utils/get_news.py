#!/usr/bin/env python3
"""
Main news fetching utility
Usage: python get_news.py [--category <category>] [--country <country>] [--limit <number>]
"""

import argparse
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from news_parser import NewsSources, NewsParser, NewsCategory


def main():
    parser = argparse.ArgumentParser(description='Fetch news from various sources')
    parser.add_argument('--category', type=str, help='News category (politics, economy, technology, etc.)')
    parser.add_argument('--country', type=str, help='Country code (KZ, RU, US, etc.)')
    parser.add_argument('--limit', type=int, default=10, help='Maximum number of news items')
    parser.add_argument('--format', type=str, choices=['text', 'json', 'brief'], default='text', 
                       help='Output format')
    parser.add_argument('--output', type=str, help='Output file path')
    
    args = parser.parse_args()
    
    # Initialize
    sources = NewsSources()
    parser_obj = NewsParser(timeout=10)
    
    # Select sources
    if args.category:
        try:
            category = NewsCategory(args.category.lower())
            selected_sources = sources.get_by_category(category)
            print(f"📁 Category: {category.value} ({len(selected_sources)} sources)")
        except ValueError:
            print(f"❌ Invalid category. Available: {[c.value for c in NewsCategory]}")
            return 1
    elif args.country:
        selected_sources = sources.get_by_country(args.country.upper())
        print(f"🇺🇳 Country: {args.country} ({len(selected_sources)} sources)")
    else:
        # Default: high priority sources
        selected_sources = sources.get_priority_sources(min_priority=7)
        print(f"📡 All high priority sources ({len(selected_sources)} sources)")
    
    if not selected_sources:
        print("❌ No active sources found for the given criteria")
        return 1
    
    # Fetch news
    print(f"📰 Fetching news from {len(selected_sources)} sources...")
    news_items = parser_obj.fetch_news(selected_sources, limit_per_source=5)
    
    if not news_items:
        print("❌ No news fetched. Check internet connection or source availability.")
        return 1
    
    print(f"✅ Fetched {len(news_items)} news items")
    
    # Output
    if args.format == 'json':
        output = {
            'metadata': {
                'fetched_at': datetime.now().isoformat(),
                'criteria': {
                    'category': args.category,
                    'country': args.country,
                    'limit': args.limit
                },
                'total_items': len(news_items)
            },
            'news': [item.to_dict() for item in news_items[:args.limit]]
        }
        
        import json
        output_str = json.dumps(output, ensure_ascii=False, indent=2)
        
    elif args.format == 'brief':
        output = f"📰 Latest News ({len(news_items)} items)\n\n"
        for i, item in enumerate(news_items[:args.limit], 1):
            output += f"{i}. {item.title}\n"
            output += f"   📍 {item.source}"
            if item.country:
                output += f" ({item.country})"
            output += f"\n   🔗 {item.url}\n\n"
    
    else:  # text format (default)
        output = parser_obj.format_for_display(news_items, limit=args.limit)
    
    # Save or print
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output)
        print(f"💾 Output saved to {args.output}")
    else:
        print("\n" + "="*60)
        print(output)
        print("="*60)
    
    return 0


if __name__ == '__main__':
    from datetime import datetime
    sys.exit(main())