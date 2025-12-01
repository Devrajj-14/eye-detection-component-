#!/bin/bash

echo "🎯 Starting Screen Calibration System"
echo "======================================"
echo ""
echo "Instructions:"
echo "1. Look at each RED circle that appears"
echo "2. Press SPACE to capture (5 times per circle)"
echo "3. Repeat for all 9 circles"
echo "4. Press 's' to save when complete"
echo ""
echo "Time: 2-3 minutes"
echo "======================================"
echo ""

# Activate virtual environment and run calibration
source venv/bin/activate
python calibrate_screen.py
