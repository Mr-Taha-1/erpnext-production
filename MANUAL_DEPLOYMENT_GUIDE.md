# 📖 ERPNext Manual Deployment Guide for Digital Ocean

## ⚠️ Authentication Required

The automated deployment script failed because Digital Ocean CLI authentication is required. Follow this manual guide to deploy ERPNext successfully.

---

## 📋 Prerequisites

1. **Digital Ocean Account** ✅ (You have this)
2. **Digital Ocean CLI (doctl)** - Install and authenticate
3. **Git** - For repository management
4. **Docker** (optional) - For local testing

---

## 🔧 Step 1: Install and Authenticate Digital Ocean CLI

### Install doctl (if not already installed)

**Windows (PowerShell as Administrator):**
```powershell
# Using Chocolatey
choco install doctl

# OR using Scoop
scoop install doctl

# OR download directly from GitHub
# https://github.com/digitalocean/doctl/releases
```

**Verify Installation:**
```bash
doctl version
```

### Authenticate with Digital Ocean

1. **Get API Token:**
   - Go to https://cloud.digitalocean.com/account/api/tokens
   - Click "Generate New Token"
   - Name: `ERPNext Deployment`
   - Scopes: `Read` and `Write`
   - Copy the token (save it securely)

2. **Authenticate doctl:**
```bash
doctl auth init
# Paste your API token when prompted
```

3. **Verify Authentication:**
```bash
doctl account get
```

---

## 🏗️ Step 2: Create Infrastructure (Manual via Web Interface)

### Option A: Using Digital Ocean Web Interface (Recommended)

#### 2.1 Create Managed Database

1. Go to https://cloud.digitalocean.com/databases
2. Click "Create Database Cluster"
3. **Configuration:**
   - **Engine:** PostgreSQL
   - **Version:** 15
   - **Size:** Basic - 2 vCPU, 4 GB RAM ($60/month)
   - **Region:** New York 3 (or closest to your users)
   - **Database Name:** `erpnext-db`
   - **Cluster Name:** `erpnext-database`

4. Click "Create Database Cluster"
5. **Save Connection Details:**
   - Host
   - Port
   - Username
   - Password
   - Database Name

#### 2.2 Create Redis Cache

1. Go to https://cloud.digitalocean.com/databases
2. Click "Create Database Cluster"
3. **Configuration:**
   - **Engine:** Redis
   - **Version:** 7
   - **Size:** Basic - 1 vCPU, 1 GB RAM ($15/month)
   - **Region:** Same as PostgreSQL
   - **Cluster Name:** `erpnext-redis`

4. Click "Create Database Cluster"
5. **Save Connection Details:**
   - Host
   - Port
   - Password

### Option B: Using CLI (After Authentication)

```bash
# Create PostgreSQL Database
doctl databases create erpnext-db \
  --engine postgres \
  --version 15 \
  --size db-s-2vcpu-4gb \
  --region nyc3 \
  --num-nodes 1

# Create Redis Cache
doctl databases create erpnext-redis \
  --engine redis \
  --version 7 \
  --size db-s-1vcpu-1gb \
  --region nyc3

# Get connection details
doctl databases connection erpnext-db
doctl databases connection erpnext-redis
```

---

## 🚀 Step 3: Deploy Application using App Platform

### 3.1 Use This Repository

This repository (`Mr-Taha-1/erpnext-production`) is already prepared with all necessary files:
- `Dockerfile` - Container configuration
- `.do/app.yaml` - App Platform specification
- `startup.sh` - Application startup script
- `requirements.txt` - Python dependencies
- `README.md` - Documentation

### 3.2 Deploy via Digital Ocean App Platform

#### Method A: Web Interface (Recommended)

1. Go to https://cloud.digitalocean.com/apps
2. Click "Create App"
3. **Source Code:**
   - **Source:** GitHub
   - **Repository:** `Mr-Taha-1/erpnext-production`
   - **Branch:** `main`
   - **Autodeploy:** Enable

4. **Configure Service:**
   - **Service Type:** Web Service
   - **Name:** `erpnext-web`
   - **Source Directory:** `/`
   - **Dockerfile Path:** `Dockerfile`
   - **HTTP Port:** `8000`
   - **Instance Size:** Professional XS ($12/month)
   - **Instance Count:** 1

5. **Environment Variables:**
   Add these environment variables (use your database connection details):
   ```
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
   SOCKETIO_PORT=9000
   DEVELOPER_MODE=0
   ```

6. **Review and Create:**
   - Review all settings
   - Click "Create Resources"

#### Method B: Using CLI (After Authentication)

```bash
# Clone this repository
git clone https://github.com/Mr-Taha-1/erpnext-production.git
cd erpnext-production

# Update app.yaml with your database details
# Edit .do/app.yaml and replace placeholder values

# Deploy using app spec
doctl apps create --spec .do/app.yaml

# Monitor deployment
doctl apps list
doctl apps get <app-id>
```

---

## 📊 Step 4: Monitor Deployment

### Check Deployment Status

1. **Via Web Interface:**
   - Go to https://cloud.digitalocean.com/apps
   - Click on your app
   - Monitor the "Activity" tab

2. **Via CLI:**
```bash
doctl apps list
doctl apps get <app-id>
doctl apps logs <app-id> --type=deploy
```

### Expected Deployment Time
- **Build Phase:** 5-10 minutes
- **Deploy Phase:** 3-5 minutes
- **Total:** 10-15 minutes

---

## 🌐 Step 5: Access Your Application

1. **Get Application URL:**
   - From App Platform dashboard
   - Or via CLI: `doctl apps get <app-id>`

2. **First Access:**
   - Open the application URL
   - Wait for ERPNext to initialize (may take 2-3 minutes)
   - Complete the setup wizard

3. **Login Credentials:**
   - **Username:** Administrator
   - **Password:** admin123 (or what you set in ADMIN_PASSWORD)

---

## 🔒 Step 6: Security Configuration

### 6.1 SSL Certificate
- Digital Ocean App Platform automatically provides SSL certificates
- Your app will be accessible via HTTPS

### 6.2 Database Security
1. **Firewall Rules:**
   - Go to your database cluster settings
   - Add your App Platform to trusted sources
   - Remove any unnecessary IP addresses

2. **Connection Security:**
   - All connections use SSL by default
   - Database credentials are managed securely

### 6.3 Application Security
1. **Change Default Password:**
   - Login to ERPNext
   - Go to User settings
   - Change the Administrator password

2. **Enable Two-Factor Authentication:**
   - Go to User settings
   - Enable 2FA for admin account

---

## 💰 Cost Breakdown

| Service | Configuration | Monthly Cost |
|---------|---------------|-------------|
| App Platform | Professional XS | $12 |
| PostgreSQL | 2 vCPU, 4GB RAM | $60 |
| Redis | 1 vCPU, 1GB RAM | $15 |
| **Total** | | **$87/month** |

---

## 🔧 Troubleshooting

### Common Issues

1. **Build Fails:**
   - Check build logs in App Platform
   - Verify Dockerfile syntax
   - Ensure all files are in repository

2. **Database Connection Issues:**
   - Verify database credentials
   - Check firewall settings
   - Ensure database is in same region

3. **Application Won't Start:**
   - Check application logs
   - Verify environment variables
   - Check Redis connectivity

### Getting Logs

```bash
# Application logs
doctl apps logs <app-id> --type=run

# Build logs
doctl apps logs <app-id> --type=build

# Deploy logs
doctl apps logs <app-id> --type=deploy
```

---

## ✅ Success Checklist

- [ ] Digital Ocean CLI authenticated
- [ ] PostgreSQL database created and accessible
- [ ] Redis cache created and accessible
- [ ] App Platform application deployed
- [ ] Environment variables configured
- [ ] Application accessible via HTTPS
- [ ] ERPNext setup wizard completed
- [ ] Admin password changed
- [ ] Basic security configured

---

## 🚀 Next Steps

1. **Complete ERPNext Setup:**
   - Configure company details
   - Set up users and permissions
   - Configure modules as needed

2. **Backup Strategy:**
   - Enable automatic database backups
   - Set up regular data exports

3. **Monitoring:**
   - Set up uptime monitoring
   - Configure alert notifications

4. **Performance Optimization:**
   - Monitor resource usage
   - Scale services as needed

---

## 📞 Support

- **ERPNext Documentation:** https://docs.erpnext.com/
- **Digital Ocean Support:** https://docs.digitalocean.com/
- **Community Forum:** https://discuss.erpnext.com/

---

**🎉 Congratulations! Your ERPNext system should now be running on Digital Ocean!**
