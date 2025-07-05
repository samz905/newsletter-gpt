from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import os
import json
import time

from config import (
    DEFAULT_MODEL, DATA_DIR, 
    WEEKLY_DIGEST_GENRE_INTERVAL, WEEKLY_DIGEST_RETRY_ATTEMPTS, WEEKLY_DIGEST_RETRY_INTERVAL,
    WEEKLY_DIGEST_TEST_MODE, WEEKLY_DIGEST_TEST_GENRE_INTERVAL, WEEKLY_DIGEST_TEST_RETRY_INTERVAL
)
from openai_client import chat_completion
from processors.weekly_data_extractor import WeeklyDataExtractor, Document


class WeeklyDigestGenerator:
    def __init__(self, model: str = None):
        self.model = model or DEFAULT_MODEL
        self.data_extractor = WeeklyDataExtractor()
        self.ensure_digest_directory()
    
    def ensure_digest_directory(self):
        """Ensure the digests directory exists"""
        digest_dir = os.path.join(DATA_DIR, "digests")
        if not os.path.exists(digest_dir):
            os.makedirs(digest_dir)
            print(f"📁 Created digest directory: {digest_dir}")
    
    def _get_rate_limiting_intervals(self) -> Tuple[int, int]:
        """Get the appropriate rate limiting intervals based on test mode"""
        if WEEKLY_DIGEST_TEST_MODE:
            return WEEKLY_DIGEST_TEST_GENRE_INTERVAL, WEEKLY_DIGEST_TEST_RETRY_INTERVAL
        else:
            return WEEKLY_DIGEST_GENRE_INTERVAL, WEEKLY_DIGEST_RETRY_INTERVAL
    
    def generate_weekly_digest(self, days_back: int = 7) -> Optional[str]:
        """
        Generate complete weekly digest from last N days of newsletters
        
        Args:
            days_back: Number of days to look back (default: 7)
            
        Returns:
            str: Path to generated digest file, or None if failed
        """
        print(f"📰 Generating weekly digest from last {days_back} days...")
        
        try:
            # Step 1: Extract and group newsletter data by genre
            document_groups = self.data_extractor.extract_weekly_data(days_back)
            
            if not document_groups:
                print("⚠️  No newsletters found for digest generation")
                return None
            
            # Step 2: Create genre summaries
            genre_summaries = self._create_genre_summaries(document_groups)
            
            if not genre_summaries:
                print("❌ Failed to create genre summaries")
                return None
            
            # Step 3: Create weekly digest narrative
            weekly_digest_content = self._create_weekly_digest_narrative(genre_summaries, document_groups)
            
            if not weekly_digest_content:
                print("❌ Failed to create weekly digest narrative")
                return None
            
            # Step 4: Format and save digest
            digest_path = self._save_digest(weekly_digest_content, days_back)
            
            if digest_path:
                print(f"✅ Weekly digest generated successfully: {digest_path}")
                return digest_path
            else:
                print("❌ Failed to save weekly digest")
                return None
                
        except Exception as e:
            print(f"❌ Weekly digest generation failed: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _create_genre_summaries(self, document_groups: Dict[str, List[Document]]) -> Dict[str, str]:
        """Create unified, comprehensive summaries for each genre with rate limiting"""
        genre_interval, retry_interval = self._get_rate_limiting_intervals()
        mode_info = "TEST MODE" if WEEKLY_DIGEST_TEST_MODE else "PRODUCTION MODE"
        
        print(f"📝 Creating genre summaries with rate limiting ({mode_info})...")
        print(f"⏱️  Rate limiting: {genre_interval/60:.1f} minutes between genres, {WEEKLY_DIGEST_RETRY_ATTEMPTS} retries at {retry_interval/60:.1f} minute intervals")
        
        genre_summaries = {}
        genre_list = list(document_groups.keys())
        
        for i, (genre, documents) in enumerate(document_groups.items()):
            print(f"\n🏷️  Processing {genre} ({len(documents)} newsletters) - {i+1}/{len(genre_list)}")
            
            # Create genre summary with retry logic
            genre_summary = self._create_single_genre_summary_with_retries(genre, documents)
            
            if genre_summary:
                genre_summaries[genre] = genre_summary
                print(f"✅ {genre} summary created ({len(genre_summary)} characters)")
            else:
                print(f"❌ Failed to create {genre} summary after all retries")
            
            # Rate limiting - wait between genres (except for the last one)
            if i < len(genre_list) - 1:
                print(f"⏳ Waiting {genre_interval/60:.1f} minutes before next genre...")
                time.sleep(genre_interval)
        
        print(f"\n📊 Created {len(genre_summaries)} genre summaries")
        return genre_summaries
    
    def _create_single_genre_summary_with_retries(self, genre: str, documents: List[Document]) -> Optional[str]:
        """Create a comprehensive summary for a single genre with retry logic"""
        _, retry_interval = self._get_rate_limiting_intervals()
        
        for attempt in range(WEEKLY_DIGEST_RETRY_ATTEMPTS + 1):  # +1 for initial attempt
            try:
                if attempt > 0:
                    print(f"🔄 {genre} retry attempt {attempt}/{WEEKLY_DIGEST_RETRY_ATTEMPTS}")
                
                # Try to create the summary
                summary = self._create_single_genre_summary(genre, documents)
                
                if summary:
                    if attempt > 0:
                        print(f"✅ {genre} succeeded on retry {attempt}")
                    return summary
                else:
                    print(f"⚠️  {genre} attempt {attempt + 1} failed: No summary generated")
                    
            except Exception as e:
                print(f"❌ {genre} attempt {attempt + 1} error: {e}")
            
            # Wait before retry (except for last attempt)
            if attempt < WEEKLY_DIGEST_RETRY_ATTEMPTS:
                print(f"⏳ Waiting {retry_interval/60:.1f} minutes before retry...")
                time.sleep(retry_interval)
        
        return None
    
    def _create_single_genre_summary(self, genre: str, documents: List[Document]) -> Optional[str]:
        """Create a comprehensive summary for a single genre"""
        
        # Prepare all newsletter content for this genre
        newsletter_content = []
        for i, doc in enumerate(documents, 1):
            newsletter_content.append(f"""
Newsletter {i}:
Subject: {doc.metadata.get('subject', 'No Subject')}
From: {doc.metadata.get('sender', 'Unknown')}
Date: {doc.metadata.get('date', 'Unknown')}
Summary: {doc.page_content}
""")
        
        newsletters_text = "\n".join(newsletter_content)
        
        # Create LLM prompt for genre summary
        prompt = f"""
You are an expert newsletter curator creating a comprehensive weekly digest summary for the {genre} genre.

Your task is to create a unified, comprehensive, and non-redundant summary that captures all the key insights, trends, and important information from these {len(documents)} newsletters.

GUIDELINES:
1. CREATE A COHESIVE NARRATIVE: Don't just list summaries - weave the information together into a flowing narrative
2. IDENTIFY COMMON THEMES: Look for patterns, trends, and connections across the newsletters
3. HIGHLIGHT KEY INSIGHTS: Focus on the most valuable and actionable information
4. AVOID REDUNDANCY: If multiple newsletters cover the same topic, synthesize them into one coherent discussion
5. MAINTAIN CONTEXT: Include specific details, examples, and data points that add value
6. BE COMPREHENSIVE: Don't truncate or skip information - use the full content provided
7. WRITE ENGAGINGLY: Make it interesting and readable for someone who wants to stay informed

NEWSLETTERS TO SYNTHESIZE:
{newsletters_text}

Create a comprehensive {genre} summary that would be valuable for someone who wants to understand the week's key developments in this area. Write in a clear, engaging style that flows naturally.

RESPOND WITH THE SUMMARY ONLY - NO PREFIXES OR EXPLANATIONS.
"""
        
        try:
            response = chat_completion([{"role": "user", "content": prompt}], model=self.model)
            
            if response and len(response.strip()) > 50:  # Ensure we got a substantial response
                return response.strip()
            else:
                print(f"⚠️  Received inadequate response for {genre}")
                return None
                
        except Exception as e:
            print(f"❌ LLM error for {genre}: {e}")
            return None
    
    def _create_weekly_digest_narrative(self, genre_summaries: Dict[str, str], document_groups: Dict[str, List[Document]]) -> Optional[str]:
        """Create the final weekly digest narrative from genre summaries with retry logic"""
        _, retry_interval = self._get_rate_limiting_intervals()
        print("📖 Creating weekly digest narrative with retry logic...")
        
        for attempt in range(WEEKLY_DIGEST_RETRY_ATTEMPTS + 1):  # +1 for initial attempt
            try:
                if attempt > 0:
                    print(f"🔄 Weekly digest retry attempt {attempt}/{WEEKLY_DIGEST_RETRY_ATTEMPTS}")
                
                # Try to create the digest narrative
                narrative = self._create_digest_narrative_content(genre_summaries, document_groups)
                
                if narrative:
                    if attempt > 0:
                        print(f"✅ Weekly digest succeeded on retry {attempt}")
                    return narrative
                else:
                    print(f"⚠️  Weekly digest attempt {attempt + 1} failed: No narrative generated")
                    
            except Exception as e:
                print(f"❌ Weekly digest attempt {attempt + 1} error: {e}")
            
            # Wait before retry (except for last attempt)
            if attempt < WEEKLY_DIGEST_RETRY_ATTEMPTS:
                print(f"⏳ Waiting {retry_interval/60:.1f} minutes before retry...")
                time.sleep(retry_interval)
        
        return None
    
    def _create_digest_narrative_content(self, genre_summaries: Dict[str, str], document_groups: Dict[str, List[Document]]) -> Optional[str]:
        """Create the actual digest narrative content"""
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        date_range = f"{start_date.strftime('%B %d')} - {end_date.strftime('%B %d, %Y')}"
        
        # Calculate statistics
        total_newsletters = sum(len(docs) for docs in document_groups.values())
        total_words = sum(len(summary) for summary in genre_summaries.values())
        
        # Prepare genre summaries for LLM
        genre_content = []
        for genre, summary in genre_summaries.items():
            newsletter_count = len(document_groups[genre])
            genre_content.append(f"""
## {genre}
*{newsletter_count} newsletters*

{summary}
""")
        
        genre_sections = "\n".join(genre_content)
        
        # Create LLM prompt for weekly digest
        prompt = f"""
You are a professional newsletter curator creating a comprehensive weekly digest for busy professionals.

Your task is to create an engaging, cohesive weekly digest that presents the key insights and trends from this week's newsletters in a compelling narrative format.

GUIDELINES:
1. CREATE AN ENGAGING INTRODUCTION: Start with a compelling overview that highlights the week's major themes
2. PRESENT GENRE SECTIONS: Each genre should be a well-formatted section with clear headings
3. IDENTIFY CROSS-GENRE CONNECTIONS: Look for themes that span multiple genres and highlight them
4. MAINTAIN PROFESSIONAL TONE: Write for busy professionals who want high-value insights
5. PRESERVE ALL CONTENT: Don't truncate or summarize the genre summaries - use them in full
6. ADD CONTEXT: Provide thoughtful transitions between sections
7. CONCLUDE MEANINGFULLY: End with key takeaways or forward-looking insights

DIGEST METADATA:
- Date Range: {date_range}
- Total Newsletters: {total_newsletters}
- Genres Covered: {len(genre_summaries)}

GENRE SUMMARIES TO INCORPORATE:
{genre_sections}

Create a comprehensive weekly digest that would be valuable for busy professionals. Use proper markdown formatting with clear headings and sections.

RESPOND WITH THE COMPLETE DIGEST IN MARKDOWN FORMAT.
"""
        
        response = chat_completion([{"role": "user", "content": prompt}], model=self.model)
        
        if response and len(response.strip()) > 200:  # Ensure we got a substantial response
            return response.strip()
        else:
            print("⚠️  Received inadequate digest response")
            return None
    
    def _save_digest(self, digest_content: str, days_back: int) -> Optional[str]:
        """Save the digest to a markdown file"""
        print("💾 Saving weekly digest...")
        
        try:
            # Create filename with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"weekly_digest_{timestamp}.md"
            
            # Full path
            digest_dir = os.path.join(DATA_DIR, "digests")
            file_path = os.path.join(digest_dir, filename)
            
            # Add metadata header
            metadata_header = f"""---
title: Weekly Newsletter Digest
date: {datetime.now().strftime('%Y-%m-%d')}
days_covered: {days_back}
generated_at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
model: {self.model}
---

"""
            
            # Combine header and content
            full_content = metadata_header + digest_content
            
            # Save file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(full_content)
            
            print(f"✅ Digest saved to: {file_path}")
            return file_path
            
        except Exception as e:
            print(f"❌ Error saving digest: {e}")
            return None
    
    def get_recent_digests(self, limit: int = 5) -> List[str]:
        """Get list of recent digest files"""
        digest_dir = os.path.join(DATA_DIR, "digests")
        
        if not os.path.exists(digest_dir):
            return []
        
        # Get all digest files
        digest_files = [f for f in os.listdir(digest_dir) if f.endswith('.md')]
        
        # Sort by creation time (most recent first)
        digest_files.sort(key=lambda x: os.path.getctime(os.path.join(digest_dir, x)), reverse=True)
        
        # Return full paths
        return [os.path.join(digest_dir, f) for f in digest_files[:limit]]
    
    def preview_digest_generation(self, days_back: int = 7) -> Dict:
        """Preview what would be generated without actually creating the digest"""
        print(f"👁️  Previewing digest generation for last {days_back} days...")
        
        # Get data summary
        summary = self.data_extractor.get_date_range_summary(days_back)
        
        preview = {
            'date_range': summary['date_range'],
            'total_newsletters': summary['total_newsletters'],
            'genres': summary['genres'],
            'date_distribution': summary['date_distribution'],
            'estimated_sections': len(summary['genres']),
            'ready_for_generation': summary['total_newsletters'] > 0
        }
        
        print(f"📊 Preview results:")
        print(f"   Date range: {preview['date_range'][0]} to {preview['date_range'][1]}")
        print(f"   Total newsletters: {preview['total_newsletters']}")
        print(f"   Genres: {list(preview['genres'].keys())}")
        print(f"   Ready for generation: {preview['ready_for_generation']}")
        
        return preview


def main():
    """Test the weekly digest generator"""
    print("🧪 Testing Weekly Digest Generator")
    print("=" * 50)
    
    generator = WeeklyDigestGenerator()
    
    # Test 1: Preview generation
    print("\n👁️  Test 1: Preview Digest Generation")
    preview = generator.preview_digest_generation(days_back=7)
    
    if preview['ready_for_generation']:
        print("✅ Ready for digest generation!")
        
        # Ask user if they want to generate the actual digest
        response = input("\n🤔 Generate actual weekly digest? This will make LLM API calls. (y/N): ")
        if response.lower() == 'y':
            print("\n📰 Test 2: Generate Weekly Digest")
            digest_path = generator.generate_weekly_digest(days_back=7)
            
            if digest_path:
                print(f"✅ Digest generated successfully!")
                print(f"📄 File: {digest_path}")
                
                # Show first 500 characters
                try:
                    with open(digest_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        print(f"\n📖 Preview (first 500 chars):")
                        print(content[:500] + "...")
                except Exception as e:
                    print(f"❌ Error reading digest: {e}")
            else:
                print("❌ Digest generation failed")
        else:
            print("⏭️  Skipping digest generation")
    else:
        print("⚠️  Not ready for digest generation - no newsletters found")
    
    # Test 3: Show recent digests
    print("\n📚 Test 3: Recent Digests")
    recent_digests = generator.get_recent_digests(limit=3)
    if recent_digests:
        print(f"Found {len(recent_digests)} recent digests:")
        for digest_path in recent_digests:
            print(f"   - {os.path.basename(digest_path)}")
    else:
        print("No recent digests found")
    
    print("\n✅ Weekly digest generator test complete!")
    print("=" * 50)


if __name__ == "__main__":
    main() 