"""
Notion Publisher for Newsletter GPT
Publishes weekly digests to Notion with rich formatting
"""

import os
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from notion_client import Client
from notion_client.errors import APIResponseError
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NotionPublisher:
    """
    Publisher for weekly digests to Notion database
    """
    
    def __init__(self):
        """Initialize Notion client"""
        self.notion_token = os.getenv("NOTION_TOKEN")
        self.database_id = os.getenv("NOTION_DATABASE_ID")
        
        if not self.notion_token:
            raise ValueError("NOTION_TOKEN environment variable is required")
        if not self.database_id:
            raise ValueError("NOTION_DATABASE_ID environment variable is required")
        
        self.client = Client(auth=self.notion_token)
        logger.info("Notion client initialized successfully")
    
    def publish_weekly_digest(self, digest_data: Dict) -> Optional[str]:
        """
        Publish weekly digest to Notion database
        
        Args:
            digest_data: Dictionary containing digest content and metadata
            
        Returns:
            Page ID if successful, None if failed
        """
        try:
            # Extract digest information
            week_start = digest_data.get('week_start')
            week_end = digest_data.get('week_end')
            total_newsletters = digest_data.get('total_newsletters', 0)
            genre_summaries = digest_data.get('genre_summaries', {})
            unified_summary = digest_data.get('unified_summary', '')
            
            # Create page title
            title = f"Weekly Newsletter Digest - {week_start} to {week_end}"
            
            # Create page properties
            properties = {
                "Name": {
                    "title": [
                        {
                            "type": "text",
                            "text": {"content": title}
                        }
                    ]
                },
                "Week": {
                    "date": {
                        "start": week_start,
                        "end": week_end
                    }
                },
                "Newsletter Count": {
                    "number": total_newsletters
                },
                "Genres": {
                    "multi_select": [
                        {"name": genre} for genre in genre_summaries.keys()
                    ]
                }
            }
            
            # Create page content blocks
            children = []
            
            # Add header
            children.append({
                "object": "block",
                "type": "heading_1",
                "heading_1": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {"content": f"Weekly Newsletter Digest"}
                        }
                    ]
                }
            })
            
            # Add week info
            children.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {"content": f"📅 Week: {week_start} to {week_end}"}
                        }
                    ]
                }
            })
            
            children.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {"content": f"📊 Total Newsletters: {total_newsletters}"}
                        }
                    ]
                }
            })
            
            # Add divider
            children.append({
                "object": "block",
                "type": "divider",
                "divider": {}
            })
            
            # Add unified summary
            if unified_summary:
                children.append({
                    "object": "block",
                    "type": "heading_2",
                    "heading_2": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {"content": "🌟 Weekly Highlights"}
                            }
                        ]
                    }
                })
                
                children.append({
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {"content": unified_summary}
                            }
                        ]
                    }
                })
                
                children.append({
                    "object": "block",
                    "type": "divider",
                    "divider": {}
                })
            
            # Add genre sections
            if genre_summaries:
                children.append({
                    "object": "block",
                    "type": "heading_2",
                    "heading_2": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {"content": "📑 By Genre"}
                            }
                        ]
                    }
                })
                
                for genre, data in genre_summaries.items():
                    # Genre header
                    children.append({
                        "object": "block",
                        "type": "heading_3",
                        "heading_3": {
                            "rich_text": [
                                {
                                    "type": "text",
                                    "text": {"content": f"{self._get_genre_emoji(genre)} {genre}"}
                                }
                            ]
                        }
                    })
                    
                    # Newsletter count for this genre
                    newsletter_count = len(data.get('newsletters', []))
                    children.append({
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": [
                                {
                                    "type": "text",
                                    "text": {"content": f"📈 {newsletter_count} newsletters processed"}
                                }
                            ]
                        }
                    })
                    
                    # Genre summary
                    genre_summary = data.get('summary', '')
                    if genre_summary:
                        children.append({
                            "object": "block",
                            "type": "paragraph",
                            "paragraph": {
                                "rich_text": [
                                    {
                                        "type": "text",
                                        "text": {"content": genre_summary}
                                    }
                                ]
                            }
                        })
                    
                    # Add source newsletters
                    newsletters = data.get('newsletters', [])
                    if newsletters:
                        children.append({
                            "object": "block",
                            "type": "heading_4",
                            "heading_4": {
                                "rich_text": [
                                    {
                                        "type": "text",
                                        "text": {"content": "📚 Source Newsletters"}
                                    }
                                ]
                            }
                        })
                        
                        for newsletter in newsletters[:5]:  # Limit to 5 per genre
                            subject = newsletter.get('subject', 'Unknown')
                            from_email = newsletter.get('from', 'Unknown')
                            children.append({
                                "object": "block",
                                "type": "bulleted_list_item",
                                "bulleted_list_item": {
                                    "rich_text": [
                                        {
                                            "type": "text",
                                            "text": {"content": f"{subject} (from {from_email})"}
                                        }
                                    ]
                                }
                            })
                    
                    # Add divider between genres
                    children.append({
                        "object": "block",
                        "type": "divider",
                        "divider": {}
                    })
            
            # Add footer
            children.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {"content": f"🤖 Generated by Newsletter GPT on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"}
                        }
                    ]
                }
            })
            
            # Create the page
            response = self.client.pages.create(
                parent={"database_id": self.database_id},
                properties=properties,
                children=children
            )
            
            page_id = response.get('id')
            logger.info(f"Successfully published weekly digest to Notion: {page_id}")
            return page_id
            
        except APIResponseError as e:
            logger.error(f"Notion API error: {e}")
            return None
        except Exception as e:
            logger.error(f"Error publishing to Notion: {e}")
            return None
    
    def _get_genre_emoji(self, genre: str) -> str:
        """Get appropriate emoji for genre"""
        emoji_map = {
            'Technology': '💻',
            'Business': '💼',
            'Finance': '💰',
            'Health': '🏥',
            'Education': '📚',
            'Entertainment': '🎬',
            'Sports': '⚽',
            'Politics': '🏛️',
            'Science': '🔬',
            'Travel': '✈️',
            'Food': '🍽️',
            'Fashion': '👗',
            'Gaming': '🎮',
            'Art': '🎨',
            'Music': '🎵'
        }
        return emoji_map.get(genre, '📰')
    
    def test_connection(self) -> bool:
        """Test Notion connection"""
        try:
            # Test by retrieving database info
            response = self.client.databases.retrieve(database_id=self.database_id)
            logger.info(f"Notion connection test successful: {response.get('title', [{}])[0].get('plain_text', 'Database')}")
            return True
        except APIResponseError as e:
            logger.error(f"Notion connection test failed: {e}")
            return False
        except Exception as e:
            logger.error(f"Notion connection test error: {e}")
            return False

# Test the publisher
if __name__ == "__main__":
    publisher = NotionPublisher()
    
    # Test connection
    if publisher.test_connection():
        print("✅ Notion connection successful!")
        
        # Test with sample data
        sample_data = {
            'week_start': '2024-01-15',
            'week_end': '2024-01-21',
            'total_newsletters': 12,
            'genre_summaries': {
                'Technology': {
                    'summary': 'This week in tech focused on AI advancements and new frameworks.',
                    'newsletters': [
                        {'subject': 'AI Weekly Update', 'from': 'tech@example.com'},
                        {'subject': 'Framework News', 'from': 'dev@example.com'}
                    ]
                },
                'Business': {
                    'summary': 'Business news highlighted market trends and startup funding.',
                    'newsletters': [
                        {'subject': 'Market Update', 'from': 'business@example.com'}
                    ]
                }
            },
            'unified_summary': 'This week brought exciting developments in AI and significant market movements in the business sector.'
        }
        
        page_id = publisher.publish_weekly_digest(sample_data)
        if page_id:
            print(f"✅ Test digest published successfully: {page_id}")
        else:
            print("❌ Test digest publication failed")
    else:
        print("❌ Notion connection failed") 