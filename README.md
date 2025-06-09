# 📧➡️📱 Gmail Telegram Bot Multi-Account

Automated bot that monitors multiple Gmail accounts and sends instant Telegram notifications for new messages.

## 🚀 **Key Features:**

- ✅ **Multi-account Gmail** - Monitor multiple accounts simultaneously
- ✅ **Smart filtering** - Only new messages (not all unread)
- ✅ **Advanced security** - Encrypted credentials, environment variables
- ✅ **Flexible deployment** - Windows local + cloud platforms (Railway, DigitalOcean, etc.)
- ✅ **No duplicates** - Timestamp-based filtering
- ✅ **Detailed logging** - Complete real-time monitoring
- ✅ **UTF-8 encoding** - Full support for international characters
- ✅ **Robust error handling** - Auto restart and error recovery

## 📁 **Project Structure:**

```
📦 Gmail Telegram Bot
├── 🔧 **Main Scripts:**
│   ├── test.py                    # Bot for Windows (local)
│   ├── test_server.py             # Bot for server (production)
│   └── encrypt_credentials.py     # Encrypt/decrypt credentials
│
├── ⚙️ **Configuration:**
│   ├── requirements.txt           # Dependencies for Windows
│   ├── requirements_server.txt    # Dependencies for server
│   ├── .env                       # Environment variables (local)
│   ├── .env_server                # Template for server
│   └── config_example.py          # Configuration example
│
├── 🔐 **Credentials:**
│   ├── credentials_*.json         # Gmail credentials (plain)
│   ├── credentials_*.encrypted    # Gmail credentials (encrypted)
│   └── token_*.json              # OAuth tokens (auto-generated)
│
├── 🛠️ **Utilities:**
│   ├── setup_helper.py           # Helper for initial setup
│   ├── test_config.py            # Configuration test
│   ├── start.bat                 # Windows starter (batch)
│   ├── start.ps1                 # Windows starter (PowerShell)
│   └── run_bot.ps1               # Runner with logging
│
└── 📚 **Documentation:**
    ├── README.md                 # This file
    ├── ADAUGA_CONTURI.md         # How to add new Gmail accounts
    ├── SECURITATE_SERVER.md      # Security guide for deployment
    ├── COMPARATIE_PLATFORME.md   # Platform comparison
    ├── DEPLOYMENT_GHIDURI.md     # Step-by-step deployment guides
    └── SETUP_RAILWAY.md          # Railway-specific setup
```

## 🏁 **Quick Start:**

### 🔰 **1. Local setup (Windows):**

```powershell
# Clone repository
git clone https://github.com/yourusername/gmail-bot.git
cd gmail-bot

# Install dependencies
pip install -r requirements.txt

# Configuration (follow interactive guide)
python setup_helper.py

# Test configuration
python test_config.py

# Run bot
python test.py
```

### ☁️ **2. Deploy to server (recommended: Railway):**

```bash
# 1. Push to GitHub (private repository!)
git add .
git commit -m "Ready for deployment"
git push origin main

# 2. Go to railway.app and connect your repo
# 3. Set environment variables in dashboard
# 4. Auto deploy!
```

**👉 For detailed guides, see: [`DEPLOYMENT_GHIDURI.md`](DEPLOYMENT_GHIDURI.md)**

## 📖 **Available Guides:**

| Guide | Description | For whom |
|-------|-------------|----------|
| [`ADAUGA_CONTURI.md`](ADAUGA_CONTURI.md) | How to add new Gmail accounts | Anyone |
| [`SECURITATE_SERVER.md`](SECURITATE_SERVER.md) | Security for deployment | Server deployment |
| [`COMPARATIE_PLATFORME.md`](COMPARATIE_PLATFORME.md) | Hosting platform comparison | Platform selection |
| [`DEPLOYMENT_GHIDURI.md`](DEPLOYMENT_GHIDURI.md) | Step-by-step guides for each platform | Server deployment |
| [`SETUP_RAILWAY.md`](SETUP_RAILWAY.md) | Railway-specific setup | Railway users |

## 🔧 **Detailed Configuration:**

### **Required Environment Variables:**

```bash
# Telegram Bot
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here

# Security (for server)
ENCRYPTION_PASSWORD=your_strong_password_here
```

### **Adding a new Gmail account:**

1. **Get OAuth 2.0 credentials** from Google Cloud Console
2. **Save as** `credentials_name.json`
3. **Add to code** (see [`ADAUGA_CONTURI.md`](ADAUGA_CONTURI.md))
4. **For server**: Encrypt with `encrypt_credentials.py`

## 🏆 **Recommended Platforms:**

### 🥇 **Railway** - Best overall
- ✅ 5-minute setup
- ✅ $5 free/month
- ✅ Auto-deploy from GitHub
- ✅ Secure environment variables

### 🥈 **DigitalOcean** - Maximum security  
- ✅ Full VPS control
- ✅ $6/month for 1GB RAM
- ✅ Complete SSH access
- ✅ Ideal for experts

### 🥉 **Google Cloud Run** - Cheap serverless
- ✅ Pay-per-use
- ✅ Generous free tier
- ✅ Auto scaling
- ✅ Google infrastructure

**👉 Complete comparison: [`COMPARATIE_PLATFORME.md`](COMPARATIE_PLATFORME.md)**

## 🛡️ **Security:**

### ✅ **Implemented:**
- Gmail credentials encryption with AES-256
- Environment variables for tokens
- HTML escape filtering for Telegram
- Secure logging without credentials
- Private repository recommended

### 🔐 **For production:**
- All credentials are encrypted
- Tokens in environment variables
- Firewall and SSH keys (on VPS)
- Monitoring and alerting

## 📊 **Monitoring and logging:**

### **Local (Windows):**
```
[2024-01-15 10:30:15] INFO: Bot started for 3 Gmail accounts
[2024-01-15 10:30:20] INFO: [principal@gmail.com] Check complete - 0 new messages
[2024-01-15 10:31:25] INFO: [work@gmail.com] Found 1 new message
[2024-01-15 10:31:26] SUCCESS: Message sent to Telegram
```

### **Server (Railway/DigitalOcean):**
- Real-time logs through dashboard
- Auto error alerting
- Auto restart on crash
- Performance monitoring

## 🔄 **Update and maintenance:**

### **Local update:**
```powershell
git pull origin main
pip install -r requirements.txt --upgrade
python test.py
```

### **Server update:**
- **Railway**: Auto-deploy on every GitHub commit
- **DigitalOcean**: SSH + git pull + restart service
- **Cloud platforms**: Redeploy through dashboard

## ❓ **Troubleshooting:**

### **Common issues:**

1. **"No module named 'google'"**
   ```bash
   pip install -r requirements.txt
   ```

2. **"Invalid credentials"**
   - Check `credentials_*.json` files
   - Re-run setup_helper.py

3. **"Chat not found" on Telegram**
   - Check TELEGRAM_CHAT_ID
   - Send `/start` to bot

4. **Bot doesn't find new messages**
   - Check timestamp (bot only sends messages after startup)
   - Check logs for OAuth errors

### **For advanced debugging:**
```python
# Enable detailed logging in test.py
logging.basicConfig(level=logging.DEBUG)
```

## 🤝 **Contributing:**

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 **License:**

This project is MIT licensed. See `LICENSE` for details.

## 🆘 **Support:**

- 📖 **Documentation**: Read the guides in the folder
- 🐛 **Bug reports**: Open an Issue on GitHub
- 💡 **Feature requests**: Open an Issue with "enhancement" tag
- 🔒 **Security issues**: Direct contact via email

---

**🚀 Enjoy your automated Gmail notifications! 📧➡️📱**