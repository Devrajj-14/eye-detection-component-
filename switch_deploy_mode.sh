#!/bin/bash

# Script to switch between deployment modes

echo "🚀 Interview System - Deployment Mode Switcher"
echo "=============================================="
echo ""
echo "Select deployment mode:"
echo "1) Full (Local development with dlib)"
echo "2) Deploy (Cloud without dlib)"
echo "3) Light (Minimal dependencies)"
echo "4) Restore original"
echo ""
read -p "Enter choice [1-4]: " choice

case $choice in
    1)
        echo "✅ Switching to FULL mode (local development)..."
        if [ -f "requirements-full.txt" ]; then
            cp requirements-full.txt requirements.txt
        fi
        echo "✅ Done! Use: pip install -r requirements.txt"
        ;;
    2)
        echo "✅ Switching to DEPLOY mode (cloud-friendly)..."
        cp requirements-deploy.txt requirements.txt
        echo "✅ Done! Ready for Streamlit Cloud deployment"
        echo "📝 Don't forget to commit: git add requirements.txt && git commit -m 'Deploy mode'"
        ;;
    3)
        echo "✅ Switching to LIGHT mode (minimal)..."
        cp requirements-light.txt requirements.txt
        echo "✅ Done! Minimal dependencies installed"
        ;;
    4)
        echo "✅ Restoring original requirements.txt..."
        if [ -f "requirements-full.txt" ]; then
            cp requirements-full.txt requirements.txt
        else
            echo "⚠️  No backup found. Please restore manually."
        fi
        ;;
    *)
        echo "❌ Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "Current requirements.txt:"
echo "------------------------"
head -5 requirements.txt
echo "..."
