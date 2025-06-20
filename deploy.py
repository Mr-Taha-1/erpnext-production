#!/usr/bin/env python3
"""
ERPNext Digital Ocean Deployment Script

This script automates the deployment of ERPNext on Digital Ocean App Platform.
Requires: doctl CLI authenticated with Digital Ocean API token

Usage:
    python deploy.py
"""

import subprocess
import json
import time
import sys
import os
from typing import Dict, Optional

class DigitalOceanDeployer:
    def __init__(self):
        self.region = "nyc3"
        self.postgres_name = "erpnext-postgres"
        self.redis_name = "erpnext-redis"
        self.app_name = "erpnext-production"
        
    def run_command(self, command: str, capture_output: bool = True) -> subprocess.CompletedProcess:
        """Run a shell command and return the result."""
        print(f"🔧 Running: {command}")
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=capture_output,
                text=True,
                check=True
            )
            return result
        except subprocess.CalledProcessError as e:
            print(f"❌ Command failed: {e}")
            if e.stdout:
                print(f"STDOUT: {e.stdout}")
            if e.stderr:
                print(f"STDERR: {e.stderr}")
            raise
    
    def check_doctl_auth(self) -> bool:
        """Check if doctl is authenticated."""
        try:
            result = self.run_command("doctl account get")
            print("✅ Digital Ocean CLI is authenticated")
            return True
        except subprocess.CalledProcessError:
            print("❌ Digital Ocean CLI is not authenticated")
            print("Please run: doctl auth init")
            return False
    
    def create_postgres_database(self) -> Optional[Dict]:
        """Create PostgreSQL database cluster."""
        print(f"🗄️ Creating PostgreSQL database: {self.postgres_name}")
        
        try:
            # Check if database already exists
            result = self.run_command(f"doctl databases list --format Name --no-header")
            if self.postgres_name in result.stdout:
                print(f"✅ PostgreSQL database {self.postgres_name} already exists")
                return self.get_database_info(self.postgres_name)
            
            # Create new database
            command = f"""
            doctl databases create {self.postgres_name} \
                --engine postgres \
                --version 15 \
                --size db-s-2vcpu-4gb \
                --region {self.region} \
                --num-nodes 1
            """
            
            self.run_command(command)
            print(f"✅ PostgreSQL database {self.postgres_name} created successfully")
            
            # Wait for database to be ready
            print("⏳ Waiting for database to be ready...")
            self.wait_for_database(self.postgres_name)
            
            return self.get_database_info(self.postgres_name)
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to create PostgreSQL database: {e}")
            return None
    
    def create_redis_cache(self) -> Optional[Dict]:
        """Create Redis cache cluster."""
        print(f"🔴 Creating Redis cache: {self.redis_name}")
        
        try:
            # Check if Redis already exists
            result = self.run_command(f"doctl databases list --format Name --no-header")
            if self.redis_name in result.stdout:
                print(f"✅ Redis cache {self.redis_name} already exists")
                return self.get_database_info(self.redis_name)
            
            # Create new Redis cache
            command = f"""
            doctl databases create {self.redis_name} \
                --engine redis \
                --version 7 \
                --size db-s-1vcpu-1gb \
                --region {self.region} \
                --num-nodes 1
            """
            
            self.run_command(command)
            print(f"✅ Redis cache {self.redis_name} created successfully")
            
            # Wait for Redis to be ready
            print("⏳ Waiting for Redis to be ready...")
            self.wait_for_database(self.redis_name)
            
            return self.get_database_info(self.redis_name)
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to create Redis cache: {e}")
            return None
    
    def wait_for_database(self, db_name: str, timeout: int = 600) -> bool:
        """Wait for database to be ready."""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                result = self.run_command(f"doctl databases get {db_name} --format Status --no-header")
                status = result.stdout.strip()
                
                if status == "online":
                    print(f"✅ Database {db_name} is ready")
                    return True
                
                print(f"⏳ Database {db_name} status: {status}. Waiting...")
                time.sleep(30)
                
            except subprocess.CalledProcessError:
                print(f"⏳ Waiting for database {db_name} to be available...")
                time.sleep(30)
        
        print(f"❌ Timeout waiting for database {db_name} to be ready")
        return False
    
    def get_database_info(self, db_name: str) -> Optional[Dict]:
        """Get database connection information."""
        try:
            result = self.run_command(f"doctl databases connection {db_name} --format json")
            connection_info = json.loads(result.stdout)
            return connection_info
        except (subprocess.CalledProcessError, json.JSONDecodeError) as e:
            print(f"❌ Failed to get database info for {db_name}: {e}")
            return None
    
    def create_app_spec(self, postgres_info: Dict, redis_info: Dict) -> str:
        """Create App Platform specification."""
        app_spec = {
            "name": self.app_name,
            "region": self.region,
            "services": [
                {
                    "name": "erpnext-web",
                    "source_dir": "/",
                    "dockerfile_path": "Dockerfile",
                    "github": {
                        "repo": "Mr-Taha-1/erpnext-production",
                        "branch": "main",
                        "deploy_on_push": True
                    },
                    "build_command": "echo 'Building ERPNext application...' && chmod +x startup.sh",
                    "run_command": "./startup.sh",
                    "instance_count": 1,
                    "instance_size_slug": "professional-xs",
                    "http_port": 8000,
                    "routes": [{"path": "/"}],
                    "health_check": {
                        "http_path": "/api/method/ping",
                        "initial_delay_seconds": 60,
                        "period_seconds": 30,
                        "timeout_seconds": 10,
                        "success_threshold": 1,
                        "failure_threshold": 3
                    },
                    "envs": [
                        {"key": "FRAPPE_SITE_NAME_HEADER", "value": "${APP_DOMAIN}"},
                        {"key": "ADMIN_PASSWORD", "value": "admin123"},
                        {"key": "DB_HOST", "value": postgres_info["host"]},
                        {"key": "DB_PORT", "value": str(postgres_info["port"])},
                        {"key": "DB_NAME", "value": postgres_info["database"]},
                        {"key": "DB_USER", "value": postgres_info["user"]},
                        {"key": "DB_PASSWORD", "value": postgres_info["password"]},
                        {"key": "REDIS_CACHE", "value": f"{redis_info['host']}:{redis_info['port']}"},
                        {"key": "REDIS_QUEUE", "value": f"{redis_info['host']}:{redis_info['port']}"},
                        {"key": "REDIS_SOCKETIO", "value": f"{redis_info['host']}:{redis_info['port']}"},
                        {"key": "REDIS_PASSWORD", "value": redis_info["password"]}
                    ]
                }
            ]
        }
        
        # Write app spec to file
        spec_file = "app_spec.json"
        with open(spec_file, "w") as f:
            json.dump(app_spec, f, indent=2)
        
        print(f"✅ App specification created: {spec_file}")
        return spec_file
    
    def deploy_app(self, spec_file: str) -> Optional[str]:
        """Deploy application to App Platform."""
        print(f"🚀 Deploying application: {self.app_name}")
        
        try:
            # Check if app already exists
            result = self.run_command("doctl apps list --format Name --no-header")
            if self.app_name in result.stdout:
                print(f"✅ App {self.app_name} already exists, updating...")
                # Get app ID
                result = self.run_command(f"doctl apps list --format ID,Name --no-header")
                for line in result.stdout.strip().split('\n'):
                    if self.app_name in line:
                        app_id = line.split()[0]
                        # Update existing app
                        self.run_command(f"doctl apps update {app_id} --spec {spec_file}")
                        return app_id
            
            # Create new app
            result = self.run_command(f"doctl apps create --spec {spec_file} --format ID --no-header")
            app_id = result.stdout.strip()
            
            print(f"✅ Application deployed with ID: {app_id}")
            return app_id
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to deploy application: {e}")
            return None
    
    def wait_for_deployment(self, app_id: str, timeout: int = 1200) -> bool:
        """Wait for application deployment to complete."""
        print("⏳ Waiting for deployment to complete...")
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                result = self.run_command(f"doctl apps get {app_id} --format Phase --no-header")
                phase = result.stdout.strip()
                
                if phase == "ACTIVE":
                    print("✅ Deployment completed successfully!")
                    return True
                elif phase == "ERROR":
                    print("❌ Deployment failed")
                    return False
                
                print(f"⏳ Deployment phase: {phase}. Waiting...")
                time.sleep(30)
                
            except subprocess.CalledProcessError:
                print("⏳ Checking deployment status...")
                time.sleep(30)
        
        print("❌ Timeout waiting for deployment to complete")
        return False
    
    def get_app_url(self, app_id: str) -> Optional[str]:
        """Get application URL."""
        try:
            result = self.run_command(f"doctl apps get {app_id} --format LiveURL --no-header")
            url = result.stdout.strip()
            return url
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to get app URL: {e}")
            return None
    
    def deploy(self) -> bool:
        """Main deployment function."""
        print("🚀 Starting ERPNext deployment on Digital Ocean...")
        
        # Check authentication
        if not self.check_doctl_auth():
            return False
        
        # Create PostgreSQL database
        postgres_info = self.create_postgres_database()
        if not postgres_info:
            return False
        
        # Create Redis cache
        redis_info = self.create_redis_cache()
        if not redis_info:
            return False
        
        # Create app specification
        spec_file = self.create_app_spec(postgres_info, redis_info)
        
        # Deploy application
        app_id = self.deploy_app(spec_file)
        if not app_id:
            return False
        
        # Wait for deployment
        if not self.wait_for_deployment(app_id):
            return False
        
        # Get application URL
        app_url = self.get_app_url(app_id)
        if app_url:
            print(f"\n🎉 Deployment successful!")
            print(f"📱 Application URL: {app_url}")
            print(f"👤 Login: Administrator")
            print(f"🔑 Password: admin123")
            print(f"\n📖 Complete setup guide: https://github.com/Mr-Taha-1/erpnext-production/blob/main/MANUAL_DEPLOYMENT_GUIDE.md")
        
        return True

def main():
    """Main function."""
    deployer = DigitalOceanDeployer()
    
    try:
        success = deployer.deploy()
        if success:
            print("\n✅ ERPNext deployment completed successfully!")
            sys.exit(0)
        else:
            print("\n❌ ERPNext deployment failed!")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n⚠️ Deployment interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
