# 📧➡️📱 Gmail Telegram Bot Multi-Account

Bot automat care monitorizează multiple conturi Gmail și trimite notificări instant pe Telegram pentru mesajele noi.

## 🚀 **Caracteristici principale:**

- ✅ **Multi-account Gmail** - Monitorizează mai multe conturi simultan
- ✅ **Filtrare inteligentă** - Doar mesajele noi (nu toate necitite)
- ✅ **Securitate avansată** - Credențiale criptate, environment variables
- ✅ **Deployment flexibil** - Windows local + cloud platforms (Railway, DigitalOcean, etc.)
- ✅ **Fără dubluri** - Timestamp-based filtering
- ✅ **Logging detaliat** - Monitorizare completă în timp real
- ✅ **Encoding UTF-8** - Suport complet pentru caractere românești
- ✅ **Error handling robust** - Restart automat și recuperare după erori

## 📁 **Structura proiectului:**

```
📦 Gmail Telegram Bot
├── 🔧 **Scripts principale:**
│   ├── test.py                    # Bot pentru Windows (local)
│   ├── test_server.py             # Bot pentru server (production)
│   └── encrypt_credentials.py     # Criptare/decriptare credențiale
│
├── ⚙️ **Configurare:**
│   ├── requirements.txt           # Dependencies pentru Windows
│   ├── requirements_server.txt    # Dependencies pentru server
│   ├── .env                       # Environment variables (local)
│   ├── .env_server                # Template pentru server
│   └── config_example.py          # Exemplu configurare
│
├── 🔐 **Credențiale:**
│   ├── credentials_*.json         # Credențiale Gmail (plain)
│   ├── credentials_*.encrypted    # Credențiale Gmail (criptate)
│   └── token_*.json              # Token-uri OAuth (generate automat)
│
├── 🛠️ **Utilitare:**
│   ├── setup_helper.py           # Helper pentru configurare inițială
│   ├── test_config.py            # Test configurare
│   ├── start.bat                 # Starter pentru Windows (batch)
│   ├── start.ps1                 # Starter pentru Windows (PowerShell)
│   └── run_bot.ps1               # Runner cu logging
│
└── 📚 **Documentație:**
    ├── README.md                 # Acest fișier
    ├── ADAUGA_CONTURI.md         # Cum să adaugi conturi Gmail noi
    ├── SECURITATE_SERVER.md      # Ghid securitate pentru deployment
    ├── COMPARATIE_PLATFORME.md   # Comparație platforme hosting
    ├── DEPLOYMENT_GHIDURI.md     # Ghiduri step-by-step deployment
    └── SETUP_RAILWAY.md          # Setup specific pentru Railway
```

## 🏁 **Quick Start:**

### 🔰 **1. Setup local (Windows):**

```powershell
# Clone repository
git clone https://github.com/yourusername/gmail-bot.git
cd gmail-bot

# Install dependencies
pip install -r requirements.txt

# Configurare (urmează ghidul interactiv)
python setup_helper.py

# Test configurare
python test_config.py

# Rulează bot-ul
python test.py
```

### ☁️ **2. Deploy pe server (recomandat: Railway):**

```bash
# 1. Push pe GitHub (repository privat!)
git add .
git commit -m "Ready for deployment"
git push origin main

# 2. Mergi pe railway.app și conectează repo-ul
# 3. Setează environment variables în dashboard
# 4. Deploy automat!
```

**👉 Pentru ghiduri detaliate, vezi: [`DEPLOYMENT_GHIDURI.md`](DEPLOYMENT_GHIDURI.md)**

## 📖 **Ghiduri disponibile:**

| Ghid | Descriere | Pentru cine |
|------|-----------|-------------|
| [`ADAUGA_CONTURI.md`](ADAUGA_CONTURI.md) | Cum să adaugi conturi Gmail noi | Oricine |
| [`SECURITATE_SERVER.md`](SECURITATE_SERVER.md) | Securitate pentru deployment | Server deployment |
| [`COMPARATIE_PLATFORME.md`](COMPARATIE_PLATFORME.md) | Comparație platforme hosting | Alegerea platformei |
| [`DEPLOYMENT_GHIDURI.md`](DEPLOYMENT_GHIDURI.md) | Ghiduri step-by-step pentru fiecare platformă | Deploy pe server |
| [`SETUP_RAILWAY.md`](SETUP_RAILWAY.md) | Setup specific pentru Railway | Railway users |

## 🔧 **Configurare detaliată:**

### **Environment Variables necesare:**

```bash
# Telegram Bot
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here

# Securitate (pentru server)
ENCRYPTION_PASSWORD=your_strong_password_here
```

### **Adăugarea unui cont Gmail nou:**

1. **Obține credențiale OAuth 2.0** din Google Cloud Console
2. **Salvează ca** `credentials_nume.json`
3. **Adaugă în cod** (vezi [`ADAUGA_CONTURI.md`](ADAUGA_CONTURI.md))
4. **Pentru server**: Criptează cu `encrypt_credentials.py`

## 🏆 **Platforme recomandate:**

### 🥇 **Railway** - Cel mai bun overall
- ✅ Setup în 5 minute
- ✅ $5 gratuit/lună
- ✅ Auto-deploy din GitHub
- ✅ Environment variables sigure

### 🥈 **DigitalOcean** - Securitate maximă  
- ✅ Control complet VPS
- ✅ $6/lună pentru 1GB RAM
- ✅ SSH access complet
- ✅ Ideal pentru experți

### 🥉 **Google Cloud Run** - Serverless ieftin
- ✅ Pay-per-use
- ✅ Free tier generos
- ✅ Scalare automată
- ✅ Infrastructură Google

**👉 Comparație completă: [`COMPARATIE_PLATFORME.md`](COMPARATIE_PLATFORME.md)**

## 🛡️ **Securitate:**

### ✅ **Implementat:**
- Criptare credențiale Gmail cu AES-256
- Environment variables pentru token-uri
- Filtrare HTML escape pentru Telegram
- Logging securizat fără credențiale
- Repository privat recomandat

### 🔐 **Pentru production:**
- Toate credențialele sunt criptate
- Token-uri în environment variables
- Firewall și SSH keys (pe VPS)
- Monitoring și alerting

## 📊 **Monitoring și logging:**

### **Local (Windows):**
```
[2024-01-15 10:30:15] INFO: Bot pornit pentru 3 conturi Gmail
[2024-01-15 10:30:20] INFO: [principal@gmail.com] Verificare completă - 0 mesaje noi
[2024-01-15 10:31:25] INFO: [work@gmail.com] Găsit 1 mesaj nou
[2024-01-15 10:31:26] SUCCESS: Mesaj trimis pe Telegram
```

### **Server (Railway/DigitalOcean):**
- Logs în timp real prin dashboard
- Error alerting automat
- Restart automat la crash
- Performance monitoring

## 🔄 **Update și maintenance:**

### **Update local:**
```powershell
git pull origin main
pip install -r requirements.txt --upgrade
python test.py
```

### **Update server:**
- **Railway**: Auto-deploy la fiecare commit GitHub
- **DigitalOcean**: SSH + git pull + restart service
- **Cloud platforms**: Redeploy prin dashboard

## ❓ **Troubleshooting:**

### **Probleme comune:**

1. **"No module named 'google'"**
   ```bash
   pip install -r requirements.txt
   ```

2. **"Invalid credentials"**
   - Verifică fișierele `credentials_*.json`
   - Re-run setup_helper.py

3. **"Chat not found" pe Telegram**
   - Verifică TELEGRAM_CHAT_ID
   - Scrie `/start` la bot

4. **Bot nu găsește mesaje noi**
   - Verifică timestamp-ul (bot trimite doar mesaje după pornire)
   - Check logs pentru erori OAuth

### **Pentru debugging avansat:**
```python
# Activează logging detaliat în test.py
logging.basicConfig(level=logging.DEBUG)
```

## 🤝 **Contribuții:**

1. Fork repository-ul
2. Creează branch pentru feature (`git checkout -b feature/amazing-feature`)
3. Commit modificările (`git commit -m 'Add amazing feature'`)
4. Push pe branch (`git push origin feature/amazing-feature`)
5. Deschide Pull Request

## 📄 **Licență:**

Acest proiect este MIT licensed. Vezi `LICENSE` pentru detalii.

## 🆘 **Support:**

- 📖 **Documentație**: Citește ghidurile din folder
- 🐛 **Bug reports**: Deschide un Issue pe GitHub
- 💡 **Feature requests**: Deschide un Issue cu tag "enhancement"
- 🔒 **Probleme de securitate**: Contact direct prin email

---

**🚀 Enjoy your automated Gmail notifications! 📧➡️📱**