#!/bin/bash

echo "================================"
echo "DSS Survey Backend - Railway Deployment"
echo "================================"
echo ""

# Step 1: Login
echo "Step 1: Logging into Railway..."
echo "(This will open your browser for authentication)"
railway login

if [ $? -ne 0 ]; then
    echo "❌ Login failed. Please try again."
    exit 1
fi

echo "✓ Login successful!"
echo ""

# Step 2: Initialize project
echo "Step 2: Initializing Railway project..."
railway init

if [ $? -ne 0 ]; then
    echo "❌ Initialization failed. Please try again."
    exit 1
fi

echo "✓ Project initialized!"
echo ""

# Step 3: Deploy
echo "Step 3: Deploying to Railway..."
railway up

if [ $? -ne 0 ]; then
    echo "❌ Deployment failed. Check logs with: railway logs"
    exit 1
fi

echo ""
echo "✓ Deployment successful!"
echo ""

# Step 4: Get domain
echo "Step 4: Getting your deployment URL..."
DOMAIN=$(railway domain 2>&1)

echo ""
echo "================================"
echo "🎉 DEPLOYMENT COMPLETE!"
echo "================================"
echo ""
echo "Your backend URL:"
echo "$DOMAIN"
echo ""
echo "Next steps:"
echo "1. Update followup_recommendations.html"
echo "   Replace: http://localhost:5001/api/submit"
echo "   With: https://YOUR-URL/api/submit"
echo ""
echo "2. Test your deployment:"
echo "   curl $DOMAIN/api/health"
echo ""
echo "3. View logs:"
echo "   railway logs"
echo ""
echo "================================"

