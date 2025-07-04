import email
import imaplib
from typing import Dict, Optional


class EmailParser:
    """Parse email messages and extract content"""
    
    def __init__(self, mail_connection: imaplib.IMAP4_SSL):
        self.mail = mail_connection
    
    def parse_email(self, email_id: bytes) -> Optional[Dict]:
        """Parse a single email and return structured data"""
        try:
            status, msg_data = self.mail.fetch(email_id, "(RFC822)")
            if status != 'OK':
                return None
            
            raw_email = msg_data[0][1]
            email_message = email.message_from_bytes(raw_email)
            
            # Extract basic info
            subject = email_message.get("Subject", "")
            sender = email_message.get("From", "")
            date = email_message.get("Date", "")
            
            # Get email body
            body = self._extract_body(email_message)
            
            return {
                'id': email_id.decode(),
                'subject': subject,
                'sender': sender,
                'date': date,
                'body': body  # Don't truncate body for proper filtering
            }
            
        except Exception as e:
            print(f"Error parsing email {email_id}: {e}")
            return None
    
    def _extract_body(self, email_message) -> str:
        """Extract text body from email message"""
        body = ""
        
        if email_message.is_multipart():
            for part in email_message.walk():
                if part.get_content_type() == "text/plain":
                    try:
                        body = part.get_payload(decode=True).decode('utf-8')
                        break
                    except (UnicodeDecodeError, AttributeError):
                        continue
        else:
            try:
                body = email_message.get_payload(decode=True).decode('utf-8')
            except (UnicodeDecodeError, AttributeError):
                body = str(email_message.get_payload())
        
        return body 