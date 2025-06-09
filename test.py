import os
import json
import base64
import logging
import schedule
import time
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

# Google API imports
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Telegram imports
import telegram
from telegram import Bot
from telegram.error import TelegramError

# Environment variables
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging disabled for production
logger = None

# Gmail API scopes
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


@dataclass
class EmailAccount:
    """Class for email account configuration"""

    name: str
    credentials_file: str
    token_file: str
    query: str = "is:unread"
    last_check: Optional[datetime] = None


class GmailTelegramBot:
    def __init__(self):
        self.telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID")

        if not self.telegram_bot_token or not self.telegram_chat_id:
            raise ValueError(
                "TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID must be set in .env"
            )

        self.bot = Bot(token=self.telegram_bot_token)
        self.email_accounts: List[EmailAccount] = []
        self.start_time = datetime.now()  # Time when bot started

    def add_email_account(
        self,
        name: str,
        credentials_file: str,
        token_file: str = None,
        query: str = "is:unread",
    ):
        """Add an email account for monitoring"""
        if token_file is None:
            token_file = f"{name}.json"

        account = EmailAccount(
            name=name,
            credentials_file=credentials_file,
            token_file=token_file,
            query=query,
        )
        self.email_accounts.append(account)
        pass  # Account added silently    def authenticate_gmail(self, account: EmailAccount) -> Any:
        """Gmail authentication for a specific account"""
        creds = None

        # Load existing token
        if os.path.exists(account.token_file):
            creds = Credentials.from_authorized_user_file(account.token_file, SCOPES)

        # If no valid credentials, request authentication
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(account.credentials_file):
                    return None  # Credentials file not found

                flow = InstalledAppFlow.from_client_secrets_file(
                    account.credentials_file, SCOPES
                )
                creds = flow.run_local_server(port=0)

            # Save credentials for next execution
            with open(account.token_file, "w") as token:
                token.write(creds.to_json())

        return build("gmail", "v1", credentials=creds)

    def get_email_content(self, service: Any, message_id: str) -> Dict[str, str]:
        """Extract email content"""
        try:
            message = (
                service.users().messages().get(userId="me", id=message_id).execute()
            )

            # Extract headers
            headers = message["payload"].get("headers", [])
            subject = next(
                (h["value"] for h in headers if h["name"] == "Subject"), "No subject"
            )
            sender = next(
                (h["value"] for h in headers if h["name"] == "From"),
                "Unknown sender",
            )
            date = next(
                (h["value"] for h in headers if h["name"] == "Date"), "Unknown date"
            )

            # Extract content
            body = self.extract_message_body(message["payload"])

            return {
                "id": message_id,
                "subject": subject,
                "sender": sender,
                "date": date,
                "body": body[:1000],  # Limit to 1000 characters
            }
        except Exception as e:
            return None

    def extract_message_body(self, payload: Dict) -> str:
        """Extract message body from payload"""
        body = ""

        try:
            if "parts" in payload:
                for part in payload["parts"]:
                    if part["mimeType"] == "text/plain" and "data" in part["body"]:
                        data = part["body"]["data"]
                        body = base64.urlsafe_b64decode(data).decode("utf-8")
                        break
                    elif part["mimeType"] == "text/html" and "data" in part["body"]:
                        data = part["body"]["data"]
                        body = base64.urlsafe_b64decode(data).decode("utf-8")
            elif payload["mimeType"] == "text/plain" and "data" in payload["body"]:
                data = payload["body"]["data"]
                body = base64.urlsafe_b64decode(data).decode("utf-8")
            elif payload["mimeType"] == "text/html" and "data" in payload["body"]:
                data = payload["body"]["data"]
                body = base64.urlsafe_b64decode(data).decode("utf-8")
        except Exception as e:
            body = "Could not extract message content"

        return body

    def send_telegram_message_sync(self, message: str):
        """Send message to Telegram (synchronous version, no event loop issues)"""
        try:
            # Use requests instead of async to avoid event loop issues
            import requests

            url = f"https://api.telegram.org/bot{self.telegram_bot_token}/sendMessage"
            data = {
                "chat_id": self.telegram_chat_id,
                "text": message,
                "parse_mode": "HTML",
            }

            response = requests.post(url, data=data, timeout=30)

            if response.status_code == 200:
                pass  # Success
            else:
                pass  # HTTP Error

        except Exception as e:
            pass  # Telegram error

    def send_telegram_message(self, message: str):
        """Alias for synchronous function (for compatibility)"""
        self.send_telegram_message_sync(message)

    def escape_html(self, text: str) -> str:
        """Escape HTML characters for Telegram"""
        if not text:
            return ""

        # Replace HTML special characters
        text = text.replace("&", "&amp;")
        text = text.replace("<", "&lt;")
        text = text.replace(">", "&gt;")
        text = text.replace('"', "&quot;")
        text = text.replace("'", "&#x27;")

        return text

    def format_email_message(
        self, email_data: Dict[str, str], account_name: str
    ) -> str:
        """Format message for Telegram"""
        # Escape all HTML values
        sender = self.escape_html(email_data["sender"])
        subject = self.escape_html(email_data["subject"])
        body = self.escape_html(email_data["body"])
        date = self.escape_html(email_data["date"])
        account_name = self.escape_html(account_name)

        # Shorten sender if too long
        if len(sender) > 50:
            sender = sender[:47] + "..."

        # Shorten subject if too long
        if len(subject) > 60:
            subject = subject[:57] + "..."        # Shorten message body
        if len(body) > 400:
            body = body[:397] + "..."

        message = f"""📧 <b>New email on {account_name}</b>

<b>From:</b> {sender}
<b>Subject:</b> {subject}
<b>Date:</b> {email_data['date']}

<b>Content:</b>
{body}

---
ID: {email_data['id'][:10]}..."""

        return message.strip()

    def check_emails_for_account(self, account: EmailAccount):
        """Check emails for a specific account"""
        try:
            service = self.authenticate_gmail(account)
            if not service:
                return

            # Build query with time filter
            query = account.query            # For first check, use bot start time
            # For subsequent checks, use last check time
            if account.last_check is None:
                # First check - use bot start time
                after_timestamp = int(self.start_time.timestamp())
            else:
                # Subsequent checks - use last check time
                after_timestamp = int(account.last_check.timestamp())

            query += f" after:{after_timestamp}"

            # Get message list
            results = service.users().messages().list(userId="me", q=query).execute()
            messages = results.get("messages", [])

            # Process each message
            for message in messages:
                message_id = message["id"]

                # Extract email content
                email_data = self.get_email_content(service, message_id)
                if email_data:
                    # Format and send message
                    telegram_message = self.format_email_message(
                        email_data, account.name
                    )
                    # Send message to Telegram
                    self.send_telegram_message_sync(telegram_message)

                    # Pause to avoid spam
                    time.sleep(2)
            # Actualizează timpul ultimei verificări            # Update last check time
            account.last_check = datetime.now()

        except Exception as e:
            pass  # Error checking emails

    def check_all_emails(self):
        """Check emails for all accounts"""
        for account in self.email_accounts:
            self.check_emails_for_account(account)

    def start_monitoring(self, check_interval_minutes: int = 5):
        """Start automatic monitoring"""
        # Send confirmation message to Telegram
        self.send_telegram_message_sync(
            f"🤖 <b>Gmail Bot started!</b>\n\n"
            f"⏰ Monitoring started: {self.start_time.strftime('%H:%M:%S')}\n"
            f"📧 Accounts monitored: {len(self.email_accounts)}\n"
            f"🔄 Check interval: {check_interval_minutes} min\n\n"
            f"📱 <i>You will receive notifications only for new messages!</i>"
        )

        # Schedule periodic checking
        schedule.every(check_interval_minutes).minutes.do(self.check_all_emails)

        # Run initial check after 1 minute
        # (to give time for start message to be sent)
        schedule.every(1).minutes.do(self.check_all_emails).tag("initial")        # Main loop
        try:
            while True:
                schedule.run_pending()

                # After first check, remove initial task
                if schedule.get_jobs("initial"):
                    # Check if 1 minute has passed since start
                    if datetime.now() - self.start_time > timedelta(minutes=1):
                        schedule.clear("initial")

                time.sleep(30)  # Check every 30 seconds
        except KeyboardInterrupt:
            # Send stop message to Telegram
            try:
                self.send_telegram_message_sync(
                    f"🛑 <b>Gmail Bot stopped</b>\n\n"
                    f"⏰ Stopped at: {datetime.now().strftime('%H:%M:%S')}\n"
                    f"📊 Runtime duration: {datetime.now() - self.start_time}\n\n"
                    f"👋 <i>To restart, run the script again!</i>"
                )
            except:
                pass  # Ignore errors on stop
        except Exception as e:
            pass  # Main loop error


def main():
    """Main function"""
    # Create bot instance
    bot = GmailTelegramBot()

    # Add your main Gmail account
    bot.add_email_account(
        name="kridderur@gmail.com",
        credentials_file="credentials_kridd.json",        query="is:unread",  # All NEW unread messages
    )

    # Add other Gmail accounts - uncomment and modify as needed
    bot.add_email_account(
        name="laurentiupinzaru5@gmail.com",
        credentials_file="credentials_laur5.json",  # File for 2nd account
        query="is:unread",
    )

    bot.add_email_account(
        name="pinzaru.laurentiu@usarb.md",
        credentials_file="credentials_lauru.json",  # File for work account
        query="is:unread",
    )

    # bot.add_email_account(
    #     name="📧 Personal Account",
    #     credentials_file="credentials_personal.json", # File for personal account
    #     query="is:unread"
    # )

    # Examples of advanced filters for specific accounts:
    # bot.add_email_account(
    #     name="💼 Important Messages",
    #     credentials_file="credentials_main.json",
    #     query="is:unread (is:important OR from:boss@company.com)"
    # )

    # bot.add_email_account(
    #     name="🔔 Notifications",
    #     credentials_file="credentials_main.json",
    #     query="is:unread from:(noreply@* OR notifications@*)"
    # )
    
    # Start monitoring (check every 5 minutes)
    bot.start_monitoring(check_interval_minutes=5)


if __name__ == "__main__":
    main()
