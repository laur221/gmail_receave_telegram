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

# Configure logging dezactivat pentru production
logger = None

# Gmail API scopes
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


@dataclass
class EmailAccount:
    """Clasa pentru configurarea unui cont de email"""

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
                "TELEGRAM_BOT_TOKEN și TELEGRAM_CHAT_ID trebuie să fie setate în .env"
            )

        self.bot = Bot(token=self.telegram_bot_token)
        self.email_accounts: List[EmailAccount] = []
        self.start_time = datetime.now()  # Timpul când a pornit bot-ul

    def add_email_account(
        self,
        name: str,
        credentials_file: str,
        token_file: str = None,
        query: str = "is:unread",
    ):
        """Adaugă un cont de email pentru monitorizare"""
        if token_file is None:
            token_file = f"token_{name}.json"

        account = EmailAccount(
            name=name,
            credentials_file=credentials_file,
            token_file=token_file,
            query=query,
        )
        self.email_accounts.append(account)
        pass  # Account added silently

    def authenticate_gmail(self, account: EmailAccount) -> Any:
        """Autentificare Gmail pentru un cont specific"""
        creds = None

        # Încarcă token-ul existent
        if os.path.exists(account.token_file):
            creds = Credentials.from_authorized_user_file(account.token_file, SCOPES)

        # Dacă nu există credențiale valide, solicită autentificarea
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

            # Salvează credențialele pentru următoarea execuție
            with open(account.token_file, "w") as token:
                token.write(creds.to_json())

        return build("gmail", "v1", credentials=creds)

    def get_email_content(self, service: Any, message_id: str) -> Dict[str, str]:
        """Extrage conținutul unui email"""
        try:
            message = (
                service.users().messages().get(userId="me", id=message_id).execute()
            )

            # Extrage header-ele
            headers = message["payload"].get("headers", [])
            subject = next(
                (h["value"] for h in headers if h["name"] == "Subject"), "Fără subiect"
            )
            sender = next(
                (h["value"] for h in headers if h["name"] == "From"),
                "Expeditor necunoscut",
            )
            date = next(
                (h["value"] for h in headers if h["name"] == "Date"), "Dată necunoscută"
            )

            # Extrage conținutul
            body = self.extract_message_body(message["payload"])

            return {
                "id": message_id,
                "subject": subject,
                "sender": sender,
                "date": date,
                "body": body[:1000],  # Limitează la 1000 de caractere
            }
        except Exception as e:
            return None

    def extract_message_body(self, payload: Dict) -> str:
        """Extrage corpul mesajului din payload"""
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
            body = "Nu s-a putut extrage conținutul mesajului"

        return body

    def send_telegram_message_sync(self, message: str):
        """Trimite mesaj pe Telegram (versiune sincronă, fără probleme de event loop)"""
        try:
            # Folosește requests în loc de async pentru a evita problemele cu event loop
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
        """Alias pentru funcția sincronă (pentru compatibilitate)"""
        self.send_telegram_message_sync(message)

    def escape_html(self, text: str) -> str:
        """Escapează caracterele HTML pentru Telegram"""
        if not text:
            return ""

        # Înlocuiește caracterele HTML speciale
        text = text.replace("&", "&amp;")
        text = text.replace("<", "&lt;")
        text = text.replace(">", "&gt;")
        text = text.replace('"', "&quot;")
        text = text.replace("'", "&#x27;")

        return text

    def format_email_message(
        self, email_data: Dict[str, str], account_name: str
    ) -> str:
        """Formatează mesajul pentru Telegram"""
        # Escapează toate valorile HTML
        sender = self.escape_html(email_data["sender"])
        subject = self.escape_html(email_data["subject"])
        body = self.escape_html(email_data["body"])
        date = self.escape_html(email_data["date"])
        account_name = self.escape_html(account_name)

        # Scurtează expeditorul dacă este prea lung
        if len(sender) > 50:
            sender = sender[:47] + "..."

        # Scurtează subiectul dacă este prea lung
        if len(subject) > 60:
            subject = subject[:57] + "..."

        # Scurtează corpul mesajului
        if len(body) > 400:
            body = body[:397] + "..."

        message = f"""📧 <b>Nou email pe {account_name}</b>

<b>De la:</b> {sender}
<b>Subiect:</b> {subject}
<b>Data:</b> {email_data['date']}

<b>Conținut:</b>
{body}

---
ID: {email_data['id'][:10]}..."""

        return message.strip()

    def check_emails_for_account(self, account: EmailAccount):
        """Verifică email-urile pentru un cont specific"""
        try:
            service = self.authenticate_gmail(account)
            if not service:
                return

            # Construiește query-ul cu filtru de timp
            query = account.query

            # Pentru prima verificare, folosește timpul de start al bot-ului
            # Pentru verificările următoare, folosește ultima verificare
            if account.last_check is None:
                # Prima verificare - folosește timpul de start al bot-ului
                after_timestamp = int(self.start_time.timestamp())
            else:
                # Verificări ulterioare - folosește ultima verificare
                after_timestamp = int(account.last_check.timestamp())

            query += f" after:{after_timestamp}"

            # Obține lista de mesaje
            results = service.users().messages().list(userId="me", q=query).execute()
            messages = results.get("messages", [])

            # Procesează fiecare mesaj
            for message in messages:
                message_id = message["id"]

                # Extrage conținutul email-ului
                email_data = self.get_email_content(service, message_id)
                if email_data:
                    # Formatează și trimite mesajul
                    telegram_message = self.format_email_message(
                        email_data, account.name
                    )
                    # Trimite mesajul pe Telegram
                    self.send_telegram_message_sync(telegram_message)

                    # Pauză pentru a evita spam-ul
                    time.sleep(2)
            # Actualizează timpul ultimei verificări
            account.last_check = datetime.now()

        except Exception as e:
            pass  # Error checking emails

    def check_all_emails(self):
        """Verifică email-urile pentru toate conturile"""
        for account in self.email_accounts:
            self.check_emails_for_account(account)

    def start_monitoring(self, check_interval_minutes: int = 5):
        """Începe monitorizarea automată"""
        # Trimite mesaj de confirmare pe Telegram
        self.send_telegram_message_sync(
            f"🤖 <b>Gmail Bot pornit!</b>\n\n"
            f"⏰ Început monitorizare: {self.start_time.strftime('%H:%M:%S')}\n"
            f"📧 Conturi monitorizate: {len(self.email_accounts)}\n"
            f"🔄 Interval verificare: {check_interval_minutes} min\n\n"
            f"📱 <i>Vei primi notificări doar pentru mesajele noi!</i>"
        )

        # Programează verificarea periodică
        schedule.every(check_interval_minutes).minutes.do(self.check_all_emails)

        # Rulează o verificare inițială după 1 minut
        # (pentru a da timp să se trimită mesajul de start)
        schedule.every(1).minutes.do(self.check_all_emails).tag("initial")

        # Loop principal
        try:
            while True:
                schedule.run_pending()                # După prima verificare, șterge task-ul inițial
                if schedule.get_jobs("initial"):
                    # Verifică dacă au trecut 1 minut de la start
                    if datetime.now() - self.start_time > timedelta(minutes=1):
                        schedule.clear("initial")

                time.sleep(30)  # Verifică la fiecare 30 de secunde
        except KeyboardInterrupt:
            # Trimite mesaj de oprire pe Telegram
            try:
                self.send_telegram_message_sync(
                    f"🛑 <b>Gmail Bot oprit</b>\n\n"
                    f"⏰ Oprit la: {datetime.now().strftime('%H:%M:%S')}\n"
                    f"📊 Durata funcționare: {datetime.now() - self.start_time}\n\n"
                    f"👋 <i>Pentru a reporni, rulează din nou scriptul!</i>"                )
            except:
                pass  # Ignoră erorile la oprire
        except Exception as e:
            pass  # Main loop error


def main():
    """Funcția principală"""
    # Creează instanța bot-ului
    bot = GmailTelegramBot()

    # Adaugă contul tău Gmail principal
    bot.add_email_account(
        name="📧 kridderur@gmail.com",
        credentials_file="credentials_kridd.json",
        query="is:unread",  # Toate mesajele necitite NOI
    )

    # Adaugă alte conturi Gmail - decomentează și modifică după nevoie
    bot.add_email_account(
        name="laurentiupinzaru5@gmail.com",
        credentials_file="credentials_laur5.json",  # Fișierul pentru al 2-lea cont
        query="is:unread",
    )

    bot.add_email_account(
        name="pinzaru.laurentiu@usarb.md",
        credentials_file="credentials_lauru.json",  # Fișierul pentru contul de lucru
        query="is:unread",
    )

    # bot.add_email_account(
    #     name="📧 Cont personal",
    #     credentials_file="credentials_personal.json", # Fișierul pentru contul personal
    #     query="is:unread"
    # )

    # Exemple de filtre avansate pentru conturi specifice:
    # bot.add_email_account(
    #     name="💼 Mesaje Importante",
    #     credentials_file="credentials_principal.json",
    #     query="is:unread (is:important OR from:boss@company.com)"
    # )

    # bot.add_email_account(
    #     name="🔔 Notificări",
    #     credentials_file="credentials_principal.json",
    #     query="is:unread from:(noreply@* OR notifications@*)"
    # )
    # Începe monitorizarea (verifică la fiecare 5 minute)
    bot.start_monitoring(check_interval_minutes=5)


if __name__ == "__main__":
    main()
