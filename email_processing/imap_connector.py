import imaplib
from typing import Optional


class ImapConnector:
    """Handle IMAP server connections"""
    
    def __init__(self, email_address: str, password: str, 
                 imap_server: str = "imap.gmail.com", port: int = 993):
        self.email_address = email_address
        self.password = password
        self.imap_server = imap_server
        self.port = port
        self.mail: Optional[imaplib.IMAP4_SSL] = None
    
    def connect(self) -> bool:
        """Connect to IMAP server with error handling"""
        try:
            print(f"Connecting to {self.imap_server}:{self.port}")
            self.mail = imaplib.IMAP4_SSL(self.imap_server, self.port)
            self.mail.login(self.email_address, self.password)
            print("Successfully connected to IMAP server")
            return True
        except imaplib.IMAP4.error as e:
            print(f"IMAP error: {e}")
            return False
        except Exception as e:
            print(f"Connection error: {e}")
            return False
    
    def disconnect(self):
        """Close IMAP connection"""
        if self.mail:
            try:
                self.mail.close()
                self.mail.logout()
                print("Disconnected from IMAP server")
            except Exception:
                pass
    
    def get_connection(self) -> Optional[imaplib.IMAP4_SSL]:
        """Get the IMAP connection"""
        return self.mail 