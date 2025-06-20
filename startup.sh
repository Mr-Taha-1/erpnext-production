#!/bin/bash

# ERPNext Startup Script for Digital Ocean App Platform
set -e

echo "Starting ERPNext initialization..."

# Wait for database to be ready
echo "Waiting for database connection..."
until pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER"; do
  echo "Database is unavailable - sleeping"
  sleep 2
done
echo "Database is ready!"

# Wait for Redis to be ready
echo "Waiting for Redis connection..."
until redis-cli -h "${REDIS_CACHE%%:*}" -p "${REDIS_CACHE##*:}" -a "$REDIS_PASSWORD" ping; do
  echo "Redis is unavailable - sleeping"
  sleep 2
done
echo "Redis is ready!"

# Set up Frappe bench if not exists
if [ ! -f "sites/common_site_config.json" ]; then
    echo "Setting up Frappe bench..."
    
    # Create common site config
    cat > sites/common_site_config.json << EOF
{
 "db_host": "$DB_HOST",
 "db_port": $DB_PORT,
 "db_name": "$DB_NAME",
 "db_password": "$DB_PASSWORD",
 "db_type": "postgres",
 "redis_cache": "redis://:$REDIS_PASSWORD@$REDIS_CACHE",
 "redis_queue": "redis://:$REDIS_PASSWORD@$REDIS_QUEUE",
 "redis_socketio": "redis://:$REDIS_PASSWORD@$REDIS_SOCKETIO",
 "socketio_port": 9000,
 "file_watcher_port": 6787,
 "webserver_port": 8000,
 "serve_default_site": true,
 "rebase_on_pull": false,
 "update_bench_on_update": true,
 "frappe_user": "frappe",
 "shallow_clone": true,
 "background_workers": 1,
 "use_redis_auth": true
}
EOF

    echo "Common site config created."
fi

# Create site if it doesn't exist
SITE_NAME="${FRAPPE_SITE_NAME_HEADER:-localhost}"
if [ ! -d "sites/$SITE_NAME" ]; then
    echo "Creating new site: $SITE_NAME"
    bench new-site "$SITE_NAME" \
        --db-type postgres \
        --db-host "$DB_HOST" \
        --db-port "$DB_PORT" \
        --db-name "$DB_NAME" \
        --db-password "$DB_PASSWORD" \
        --admin-password "$ADMIN_PASSWORD" \
        --no-mariadb-socket
    
    echo "Installing ERPNext app..."
    bench --site "$SITE_NAME" install-app erpnext
    
    echo "Setting up scheduler..."
    bench --site "$SITE_NAME" enable-scheduler
    
    echo "Site created successfully!"
else
    echo "Site $SITE_NAME already exists, running migrations..."
    bench --site "$SITE_NAME" migrate
fi

# Build assets
echo "Building assets..."
bench build --app erpnext

# Set permissions
echo "Setting up permissions..."
chown -R frappe:frappe /home/frappe/frappe-bench
chmod -R 755 /home/frappe/frappe-bench

# Start ERPNext
echo "Starting ERPNext server..."
exec bench start
