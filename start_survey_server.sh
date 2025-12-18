#!/bin/bash

# Simple script to start a local web server for testing the follow-up survey

echo "Starting local web server for DSS Follow-up Survey..."
echo ""
echo "The survey will be available at:"
echo "  http://localhost:8000/followup_consent.html"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python3 -m http.server 8000

