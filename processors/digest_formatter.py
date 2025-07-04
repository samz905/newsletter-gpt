from typing import List, Dict
from datetime import datetime, timedelta

class DigestFormatter:
    """Format summaries into a weekly digest"""
    
    def create_weekly_digest(self, summaries: List[Dict]) -> str:
        """Combine summaries into a weekly digest format"""
        print("📄 Creating weekly digest...")
        
        # Get date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        
        digest = self._create_header(start_date, end_date, len(summaries))
        
        for i, summary in enumerate(summaries, 1):
            digest += self._format_summary_entry(i, summary)
        
        return digest
    
    def _create_header(self, start_date: datetime, end_date: datetime, count: int) -> str:
        """Create the digest header"""
        return f"""
# Weekly Newsletter Digest
## {start_date.strftime('%B %d')} - {end_date.strftime('%B %d, %Y')}

*{count} newsletters processed*

---

"""
    
    def _format_summary_entry(self, index: int, summary: Dict) -> str:
        """Format a single summary entry"""
        return f"""
## {index}. {summary['title']}
**From:** {summary['sender']}  
**Date:** {summary['date']}

{summary['summary']}

---

""" 