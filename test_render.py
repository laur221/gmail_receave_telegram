import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_telegram_connection():
    """Test if Telegram bot token and chat ID work"""
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    if not bot_token:
        print("❌ TELEGRAM_BOT_TOKEN not found in environment")
        return False
        
    if not chat_id:
        print("❌ TELEGRAM_CHAT_ID not found in environment")
        return False
        
    print(f"✅ Bot Token: {bot_token[:10]}...{bot_token[-10:]}")
    print(f"✅ Chat ID: {chat_id}")
    
    # Test sending a message
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": "🧪 <b>Test message from Render!</b>\n\n⏰ Time: " + str(__import__('datetime').datetime.now()),
        "parse_mode": "HTML"
    }
    
    try:
        response = requests.post(url, data=data, timeout=10)
        if response.status_code == 200:
            print("✅ Telegram message sent successfully!")
            return True
        else:
            print(f"❌ Telegram error: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Telegram connection error: {e}")
        return False

def test_gmail_credentials():
    """Test if Gmail credentials files exist"""
    files_to_check = [
        "credentials_kridd.json",
        "credentials_laur5.json", 
        "credentials_lauru.json"
    ]
    
    all_exist = True
    for file in files_to_check:
        if os.path.exists(file):
            print(f"✅ {file} exists")
        else:
            print(f"❌ {file} NOT found")
            all_exist = False
            
    return all_exist

def main():
    print("🔍 Testing Render deployment configuration...\n")
    
    # Test environment variables
    port = os.getenv("PORT")
    print(f"PORT: {port}")
    
    # Test Telegram
    print("\n📱 Testing Telegram connection:")
    telegram_ok = test_telegram_connection()
    
    # Test Gmail credentials
    print("\n📧 Testing Gmail credentials:")
    gmail_ok = test_gmail_credentials()
    
    print(f"\n📊 Results:")
    print(f"Telegram: {'✅ OK' if telegram_ok else '❌ FAILED'}")
    print(f"Gmail: {'✅ OK' if gmail_ok else '❌ FAILED'}")
    
    if telegram_ok and gmail_ok:
        print("\n🎉 All tests passed! Bot should work correctly.")
    else:
        print("\n⚠️  There are configuration issues that need to be fixed.")

if __name__ == "__main__":
    main()
