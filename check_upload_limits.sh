#!/bin/bash

echo "🔍 Checking upload limits configuration..."

# Check if nginx is running
if systemctl is-active --quiet nginx; then
    echo "✅ Nginx is running"
    
    # Check nginx configuration for client_max_body_size
    echo "📋 Checking nginx client_max_body_size..."
    
    # Check main nginx.conf
    if grep -r "client_max_body_size" /etc/nginx/ 2>/dev/null; then
        echo "Found client_max_body_size settings:"
        grep -r "client_max_body_size" /etc/nginx/ 2>/dev/null
    else
        echo "❌ No client_max_body_size found in nginx config"
        echo "💡 Need to add: client_max_body_size 100M;"
    fi
    
    # Check if there's a site config for this domain
    if [ -f "/etc/nginx/sites-available/vuquangduy.online" ]; then
        echo "📄 Found site config for vuquangduy.online"
        grep -n "client_max_body_size\|proxy_pass\|location" /etc/nginx/sites-available/vuquangduy.online
    fi
    
else
    echo "ℹ️  Nginx is not running or not installed"
fi

# Check if apache is running
if systemctl is-active --quiet apache2; then
    echo "✅ Apache is running"
    echo "📋 Checking apache upload limits..."
    
    # Check for LimitRequestBody
    if grep -r "LimitRequestBody" /etc/apache2/ 2>/dev/null; then
        echo "Found LimitRequestBody settings:"
        grep -r "LimitRequestBody" /etc/apache2/ 2>/dev/null
    else
        echo "ℹ️  No LimitRequestBody found in apache config"
    fi
else
    echo "ℹ️  Apache is not running or not installed"
fi

# Check what's running on port 9005
echo "🔍 Checking what's running on port 9005..."
netstat -tlnp | grep :9005 || echo "❌ Nothing listening on port 9005"

# Check PM2 status
echo "🔍 Checking PM2 status..."
pm2 status 2>/dev/null || echo "❌ PM2 not found or no processes"

echo "✅ Check complete!"
