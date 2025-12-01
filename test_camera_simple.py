#!/usr/bin/env python3
"""
Simple camera test - Run this first to grant permissions
"""
import cv2
import sys

print("Testing camera access...")
print("=" * 50)

# Try to open camera
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("❌ FAILED: Camera not accessible")
    print("\n📋 To fix:")
    print("1. Open System Settings")
    print("2. Go to Privacy & Security > Camera")
    print("3. Enable camera for Terminal or Python")
    print("4. Run this script again")
    sys.exit(1)

print("✅ Camera opened successfully")

# Try to read a frame
ret, frame = cap.read()

if not ret:
    print("❌ FAILED: Cannot read from camera")
    cap.release()
    sys.exit(1)

print(f"✅ Frame captured: {frame.shape}")
print(f"✅ Resolution: {frame.shape[1]}x{frame.shape[0]}")

# Show camera for 3 seconds
print("\n📹 Showing camera feed for 3 seconds...")
print("Press 'q' to quit early")

import time
start_time = time.time()

while time.time() - start_time < 3:
    ret, frame = cap.read()
    if ret:
        cv2.imshow('Camera Test - Press Q to quit', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()

print("\n" + "=" * 50)
print("✅ SUCCESS: Camera is working!")
print("\nYou can now run the interview system:")
print("  streamlit run pro_interview_system.py")
