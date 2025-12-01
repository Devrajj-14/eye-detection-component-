#!/bin/bash

echo "Installing OpenFace Multi-Person Tracker..."

# Install Python dependencies
pip install -r requirements.txt

# Create directories
mkdir -p models
mkdir -p calibration
mkdir -p captures

# Download dlib face predictor
echo "Downloading facial landmark predictor..."
cd models
if [ ! -f "shape_predictor_68_face_landmarks.dat" ]; then
    curl -L -O http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2
    bunzip2 shape_predictor_68_face_landmarks.dat.bz2
    echo "Landmark predictor downloaded successfully"
else
    echo "Landmark predictor already exists"
fi

cd ..

echo "Installation complete!"
echo "Run the application with: python app.py"
