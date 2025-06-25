import imaplib
import email
import time
import telebot
import os
from dotenv import load_dotenv
from email.header import decode_header
import html2text
import threading
from flask import Flask
from datetime import datetime
import pytz

# Încarcă variabilele din .env (funcționează și pe Render)
load_dotenv()
load_dotenv('/etc/secrets/.env')  # Pentru Render Secret Files

# Configurare cont unic Gmail
GMAIL_USER = os.getenv("GMAIL_USER_1")
GMAIL_PASS = os.getenv("GMAIL_PASS_1")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Inițializează botul
bot = telebot.TeleBot(TELEGRAM_TOKEN)

# Set pentru a ține evidența emailurilor deja procesate
processed_emails = set()

# Funcție pentru a obține ora locală din Moldova
def get_moldova_time():
    """Returnează data și ora din Moldova (UTC+2/UTC+3 - același timezone cu Europa/București)"""
    moldova_tz = pytz.timezone('Europe/Bucharest')  # Moldova folosește același timezone
    utc_now = datetime.utcnow().replace(tzinfo=pytz.UTC)
    moldova_time = utc_now.astimezone(moldova_tz)
    return moldova_time

# Funcție pentru a escapa caractere speciale Markdown
def escape_markdown(text):
    """Escapează caracterele speciale pentru Markdown"""
    if not text:
        return ""
    # Caractere care trebuie escapate în Markdown
    escape_chars = ['*', '_', '`', '[', ']', '(', ')', '~', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for char in escape_chars:
        text = text.replace(char, f'\\{char}')
    return text

# Creează aplicația Flask pentru a satisface cerința de port a Render
app = Flask(__name__)

@app.route('/')
def health_check():
    moldova_time = get_moldova_time()
    return {
        "status": "Gmail Bot is running",
        "timestamp": moldova_time.strftime('%Y-%m-%d %H:%M:%S'),
        "timezone": "Europe/Bucharest (Moldova)",
        "processed_emails": len(processed_emails)
    }

@app.route('/status')
def status():
    moldova_time = get_moldova_time()
    return {
        "gmail_user": GMAIL_USER,
        "bot_active": True,
        "last_check": moldova_time.strftime('%Y-%m-%d %H:%M:%S'),
        "timezone": "Europe/Bucharest (Moldova)"
    }

@app.route('/env-check')
def env_check():
    """Verifică dacă variabilele de mediu sunt setate"""
    return {
        "GMAIL_USER_1": "SET" if GMAIL_USER else "NOT SET",
        "GMAIL_PASS_1": "SET" if GMAIL_PASS else "NOT SET",
        "TELEGRAM_TOKEN": "SET" if TELEGRAM_TOKEN else "NOT SET", 
        "TELEGRAM_CHAT_ID": "SET" if TELEGRAM_CHAT_ID else "NOT SET",
        "all_env_vars": dict(os.environ)  # Pentru debugging complet
    }

# === FUNCTIE DE VERIFICARE EMAIL ===
def check_email(is_first_run=False):
    """Verifică emailurile pentru contul configurat"""
    if not GMAIL_USER or not GMAIL_PASS:
        print("❌ Credentialele Gmail nu sunt configurate!")
        return
    
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(GMAIL_USER, GMAIL_PASS)
        mail.select("inbox")

        status, messages = mail.search(None, '(UNSEEN)')
        email_ids = messages[0].split()
        new_emails_processed = 0

        for e_id in email_ids:
            # Creează un ID unic pentru acest email
            email_unique_id = f"{GMAIL_USER}_{e_id.decode()}"
            
            # La prima rulare, adaugă toate emailurile în set fără să le proceseze
            if is_first_run:
                processed_emails.add(email_unique_id)
                continue
            
            # Verifică dacă emailul a fost deja procesat
            if email_unique_id in processed_emails:
                continue
                
            # Adaugă emailul în set pentru a nu-l procesa din nou
            processed_emails.add(email_unique_id)
            new_emails_processed += 1

            status, msg_data = mail.fetch(e_id, "(RFC822)")
            raw_email = msg_data[0][1]
            msg = email.message_from_bytes(raw_email)

            # Decodează subiectul dacă este encodat
            subject_raw = msg["subject"] or "Fără subiect"
            subject_decoded = ""
            try:
                decoded_parts = decode_header(subject_raw)
                for part, encoding in decoded_parts:
                    if isinstance(part, bytes):
                        if encoding:
                            subject_decoded += part.decode(encoding)
                        else:
                            subject_decoded += part.decode('utf-8', errors='ignore')
                    else:
                        subject_decoded += str(part)
                subject = subject_decoded or "Fără subiect"
            except:
                subject = subject_raw

            sender = msg["from"] or "Expeditor necunoscut"
            
            # Extrage email-ul destinatar original din headers
            original_to = msg.get("To") or msg.get("Delivered-To") or msg.get("X-Original-To") or GMAIL_USER
            
            # Funcție pentru a extrage doar email-ul din format "Nume <email@domain.com>"
            def extract_email(email_string):
                if '<' in email_string and '>' in email_string:
                    start = email_string.find('<') + 1
                    end = email_string.find('>')
                    return email_string[start:end]
                return email_string
            
            # Curăță adresele de email
            sender_clean = extract_email(sender)
            original_to_clean = extract_email(original_to)

            # Extragem conținutul mesajului cu prioritate pentru text/plain
            body = ""
            html_body = ""
            
            if msg.is_multipart():
                for part in msg.walk():
                    content_type = part.get_content_type()
                    try:
                        if content_type == "text/plain" and not body:
                            body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                        elif content_type == "text/html" and not html_body:
                            html_body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                    except:
                        continue
            else:
                try:
                    content_type = msg.get_content_type()
                    if content_type == "text/plain":
                        body = msg.get_payload(decode=True).decode('utf-8', errors='ignore')
                    elif content_type == "text/html":
                        html_body = msg.get_payload(decode=True).decode('utf-8', errors='ignore')
                except:
                    body = "Conținut indisponibil"

            # Dacă nu avem text plain, convertim HTML la text
            if not body and html_body:
                try:
                    h = html2text.HTML2Text()
                    h.ignore_links = True
                    h.ignore_images = True
                    h.body_width = 0  # No line wrapping
                    body = h.handle(html_body)
                    # Clean up excessive newlines
                    body = '\n'.join(line.strip() for line in body.split('\n') if line.strip())
                except:
                    body = "Conținut HTML - nu poate fi afișat"

            # Clean and format the message body
            body_clean = body[:400] if body else "Fără conținut"
            if len(body) > 400:
                body_clean += "..."

            # Escapează textul pentru Markdown
            original_to_safe = escape_markdown(original_to_clean)
            sender_safe = escape_markdown(sender_clean)
            subject_safe = escape_markdown(subject)
            body_safe = escape_markdown(body_clean)

            # Obține ora locală din Moldova
            moldova_time = get_moldova_time()
            date_md = moldova_time.strftime('%d.%m.%Y')
            time_md = moldova_time.strftime('%H:%M:%S')

            # Format the message nicely cu text escapat pentru Markdown
            text_to_send = f"""
📧 *Email Nou Primit*
━━━━━━━━━━━━━━━━━━━━
📨 *Trimis la:* {original_to_safe}
👤 *De la:* {sender_safe}
📝 *Subiect:* {subject_safe}
📅 *Data:* {date_md}
⏰ *Ora:* {time_md}
━━━━━━━━━━━━━━━━━━━━

💬 *Conținut:*
{body_safe}

────────────────────
🤖 *Gmail Bot*
"""
            
            try:
                bot.send_message(TELEGRAM_CHAT_ID, text_to_send, parse_mode="Markdown")
            except Exception as telegram_error:
                # Dacă Markdown nu funcționează, trimite fără formatare
                print(f"⚠️ Eroare Markdown, trimit fără formatare: {telegram_error}")
                simple_text = f"""
📧 Email Nou Primit
━━━━━━━━━━━━━━━━━━━━
📨 Trimis la: {original_to_clean}
👤 De la: {sender_clean}
📝 Subiect: {subject}
📅 Data: {date_md}
⏰ Ora: {time_md}
━━━━━━━━━━━━━━━━━━━━

💬 Conținut:
{body_clean}

────────────────────
🤖 Gmail Bot
"""
                bot.send_message(TELEGRAM_CHAT_ID, simple_text)

        mail.logout()
        
        # Afișează doar dacă nu e prima rulare
        if not is_first_run:
            print(f"✅ Verificat - {new_emails_processed} emailuri noi")

    except Exception as e:
        print(f"❌ Eroare: {e}")

# === FUNCTIE PENTRU RULAREA BOTULUI IN BACKGROUND ===
def run_email_bot():
    """Rulează botul de email în background"""
    print("🚀 Pornind Gmail Bot...")
    print(f"📧 Cont configurat: {GMAIL_USER}")
    
    # Debug: Verifică toate variabilele de mediu
    print("🔍 Debug - Variabile de mediu:")
    print(f"   GMAIL_USER_1: {'SET' if GMAIL_USER else 'NOT SET'}")
    print(f"   GMAIL_PASS_1: {'SET' if GMAIL_PASS else 'NOT SET'}")  
    print(f"   TELEGRAM_TOKEN: {'SET' if TELEGRAM_TOKEN else 'NOT SET'}")
    print(f"   TELEGRAM_CHAT_ID: {'SET' if TELEGRAM_CHAT_ID else 'NOT SET'}")
    
    if not GMAIL_USER or not GMAIL_PASS:
        print("❌ Verifică configurația din fișierul .env!")
        print("💡 Pe Render, setează Environment Variables în Settings!")
        return
    
    print("\n⏰ Verificare la fiecare 30 de secunde...")
    
    # Prima rulare - marchează emailurile existente ca procesate
    print("📋 Încărcarea emailurilor existente...")
    check_email(is_first_run=True)
    print("✅ Emailurile existente au fost marcate ca procesate")
    print("🔔 Acum voi notifica doar emailurile noi care vin!\n")
    
    while True:
        try:
            print(f"🔍 Verificare emailuri - {time.strftime('%Y-%m-%d %H:%M:%S')}")
            check_email(is_first_run=False)
            time.sleep(30)  # Mărit la 30 secunde pentru Render
        except Exception as e:
            print(f"❌ Eroare generală: {e}")
            time.sleep(30)

# === MAIN ===
if __name__ == "__main__":
    # Pornește botul de email într-un thread separat
    email_thread = threading.Thread(target=run_email_bot, daemon=True)
    email_thread.start()
    
    # Pornește serverul Flask pentru a satisface cerința de port a Render
    port = int(os.environ.get('PORT', 5000))
    print(f"🌐 Pornind serverul web pe portul {port}...")
    app.run(host='0.0.0.0', port=port, debug=False)
