# ⚡ Quick Start Guide - ERPNext on Digital Ocean

## 🚀 Deploy in 3 Steps

### Step 1: Authenticate Digital Ocean CLI

```bash
# Install doctl (if not installed)
choco install doctl  # Windows
# OR
brew install doctl   # macOS
# OR
sudo snap install doctl  # Linux

# Authenticate
doctl auth init
# Enter your Digital Ocean API token when prompted
```

**Get API Token:** https://cloud.digitalocean.com/account/api/tokens

### Step 2: Run Automated Deployment

```bash
# Clone this repository
git clone https://github.com/Mr-Taha-1/erpnext-production.git
cd erpnext-production

# Run deployment script
python deploy.py
```

### Step 3: Access Your ERPNext

- Wait 10-15 minutes for deployment
- Access the provided URL
- Login with: `Administrator` / `admin123`
- Complete the setup wizard

---

## 🌐 Manual Deployment (Web Interface)

Prefer using the web interface? Follow these steps:

### 1. Create Infrastructure

**PostgreSQL Database:**
- Go to: https://cloud.digitalocean.com/databases
- Create PostgreSQL 15, 2 vCPU, 4GB RAM
- Save connection details

**Redis Cache:**
- Create Redis 7, 1 vCPU, 1GB RAM
- Save connection details

### 2. Deploy Application

**App Platform:**
- Go to: https://cloud.digitalocean.com/apps
- Connect GitHub repository: `Mr-Taha-1/erpnext-production`
- Configure environment variables with your database details
- Deploy!

---

## 📋 Environment Variables

Required for manual deployment:

```bash
DB_HOST=your-postgres-host
DB_PORT=25060
DB_NAME=defaultdb
DB_USER=doadmin
DB_PASSWORD=your-postgres-password
REDIS_CACHE=your-redis-host:25061
REDIS_QUEUE=your-redis-host:25061
REDIS_SOCKETIO=your-redis-host:25061
REDIS_PASSWORD=your-redis-password
ADMIN_PASSWORD=admin123
FRAPPE_SITE_NAME_HEADER=${APP_DOMAIN}
```

---

## 💰 Cost: ~$87/month

- App Platform: $12/month
- PostgreSQL: $60/month  
- Redis: $15/month

---

## 🆘 Need Help?

- **Detailed Guide:** [MANUAL_DEPLOYMENT_GUIDE.md](MANUAL_DEPLOYMENT_GUIDE.md)
- **ERPNext Docs:** https://docs.erpnext.com/
- **Digital Ocean Docs:** https://docs.digitalocean.com/

---

## ✅ Success Checklist

- [ ] Digital Ocean account ready
- [ ] API token generated
- [ ] `doctl` installed and authenticated
- [ ] Deployment script executed
- [ ] Application accessible
- [ ] ERPNext setup completed

**🎉 Ready to manage your business with ERPNext!**
