from typing import List, Dict
from openai_client import chat_completion

class SummaryGenerator:
    """Generate individual summaries for newsletters"""
    
    def generate_summaries(self, newsletters: List[Dict]) -> List[Dict]:
        """Generate individual summaries for each newsletter"""
        print("📝 Generating summaries...")
        
        summaries = []
        
        for newsletter in newsletters:
            summary = self._generate_single_summary(newsletter)
            if summary:
                summaries.append(summary)
        
        print(f"✅ Generated {len(summaries)} summaries")
        return summaries
    
    def _generate_single_summary(self, newsletter: Dict) -> Dict:
        """Generate summary for a single newsletter"""
        try:
            prompt = f"""
Please create a concise summary of this newsletter email:

Subject: {newsletter['subject']}
Sender: {newsletter['sender']}
Content: {newsletter['cleaned_body']}

Create a summary that:
1. Captures the main topic/theme
2. Highlights key points or insights
3. Includes all necessary details
4. Is valuable for a weekly digest

Format as a brief, engaging summary that meaningfully captures the content of the newsletter.

Simply return "Not a newsletter" if the content is not a newsletter.
"""
            
            summary_text = chat_completion([{"role": "user", "content": prompt}])
            
            summary = {
                'original_email': newsletter,
                'summary': summary_text.strip(),
                'title': newsletter['subject'],
                'sender': newsletter['sender'],
                'date': newsletter['date']
            }
            
            print(f"✅ Summarized: {newsletter['subject'][:30]}...")
            return summary
            
        except Exception as e:
            print(f"❌ Summary error for {newsletter['subject']}: {e}")
            return None 