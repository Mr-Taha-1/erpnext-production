# 🚀 ERPNext Production Deployment

## Overview

This repository contains all the necessary files to deploy ERPNext ERP system on Digital Ocean App Platform with managed PostgreSQL and Redis services.

## 🏗️ Architecture

- **Application**: ERPNext v15 (Frappe Framework)
- **Database**: PostgreSQL 15 (Managed)
- **Cache**: Redis 7 (Managed)
- **Platform**: Digital Ocean App Platform
- **SSL**: Automatic SSL certificates

## 📁 Repository Structure

```
├── Dockerfile              # Container configuration
├── .do/app.yaml           # App Platform specification
├── startup.sh             # Application startup script
├── requirements.txt       # Python dependencies
└── README.md              # This file
```

## 🚀 Quick Deploy

### Prerequisites

1. Digital Ocean account
2. GitHub account (this repository)

### Deployment Steps

1. **Create Infrastructure:**
   - PostgreSQL database (2 vCPU, 4GB RAM)
   - Redis cache (1 vCPU, 1GB RAM)

2. **Deploy Application:**
   - Connect this GitHub repository to Digital Ocean App Platform
   - Configure environment variables
   - Deploy!

### Detailed Instructions

For complete step-by-step instructions, see the [Manual Deployment Guide](MANUAL_DEPLOYMENT_GUIDE.md).

## 💰 Cost Estimate

| Service | Configuration | Monthly Cost |
|---------|---------------|-------------|
| App Platform | Professional XS | $12 |
| PostgreSQL | 2 vCPU, 4GB RAM | $60 |
| Redis | 1 vCPU, 1GB RAM | $15 |
| **Total** | | **$87/month** |

## 🔧 Environment Variables

Required environment variables for deployment:

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

## 🌐 Access Your Application

After successful deployment:

1. Access your application URL (provided by App Platform)
2. Complete the ERPNext setup wizard
3. Start using your ERP system!

## 🛠️ Support

- [ERPNext Documentation](https://docs.erpnext.com/)
- [Digital Ocean App Platform Docs](https://docs.digitalocean.com/products/app-platform/)
- [ERPNext Community Forum](https://discuss.erpnext.com/)

## 📄 License

ERPNext is licensed under GNU General Public License v3.0

---

**Ready to deploy? Follow the [Manual Deployment Guide](MANUAL_DEPLOYMENT_GUIDE.md) for detailed instructions!**
