"""
Verify installation and dependencies
"""
import sys
import os


def check_python_version():
    """Check Python version"""
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print("❌ Python 3.7+ required")
        return False
    print("✓ Python version OK")
    return True


def check_dependencies():
    """Check required packages"""
    required = {
        'cv2': 'opencv-python',
        'numpy': 'numpy',
        'scipy': 'scipy',
        'PyQt5': 'PyQt5',
        'ultralytics': 'ultralytics',
        'dlib': 'dlib',
        'sklearn': 'scikit-learn'
    }
    
    missing = []
    for module, package in required.items():
        try:
            __import__(module)
            print(f"✓ {package}")
        except ImportError:
            print(f"❌ {package} not found")
            missing.append(package)
    
    return len(missing) == 0, missing


def check_models():
    """Check model files"""
    models = {
        'models/shape_predictor_68_face_landmarks.dat': 'dlib face predictor'
    }
    
    all_present = True
    for path, name in models.items():
        if os.path.exists(path):
            print(f"✓ {name}")
        else:
            print(f"❌ {name} not found at {path}")
            all_present = False
    
    return all_present


def check_directories():
    """Check required directories"""
    dirs = ['models', 'calibration', 'captures', 'utils', 'ui']
    
    for d in dirs:
        if os.path.exists(d):
            print(f"✓ {d}/")
        else:
            print(f"❌ {d}/ not found")
            return False
    
    return True


def check_camera():
    """Check camera access"""
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        ret, frame = cap.read()
        cap.release()
        
        if ret:
            print(f"✓ Camera accessible (frame: {frame.shape})")
            return True
        else:
            print("❌ Camera not accessible")
            return False
    except Exception as e:
        print(f"❌ Camera error: {e}")
        return False


def main():
    print("=" * 60)
    print("OpenFace 3.0 Installation Verification")
    print("=" * 60)
    
    print("\n1. Checking Python version...")
    python_ok = check_python_version()
    
    print("\n2. Checking dependencies...")
    deps_ok, missing = check_dependencies()
    
    print("\n3. Checking directories...")
    dirs_ok = check_directories()
    
    print("\n4. Checking models...")
    models_ok = check_models()
    
    print("\n5. Checking camera...")
    camera_ok = check_camera()
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    if python_ok and deps_ok and dirs_ok and models_ok and camera_ok:
        print("✓ All checks passed! Ready to run.")
        print("\nRun the application:")
        print("  python app.py          # Full GUI version")
        print("  python run_simple.py   # Simple OpenCV version")
    else:
        print("❌ Some checks failed. Please fix the issues above.")
        
        if not deps_ok:
            print("\nInstall missing dependencies:")
            print(f"  pip install {' '.join(missing)}")
        
        if not models_ok:
            print("\nDownload missing models:")
            print("  bash install.sh")
            print("  # or manually:")
            print("  cd models")
            print("  wget http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2")
            print("  bunzip2 shape_predictor_68_face_landmarks.dat.bz2")
        
        if not camera_ok:
            print("\nCamera issues:")
            print("  - Check camera permissions")
            print("  - Ensure camera is not in use by another app")
            print("  - Try different camera index in code")


if __name__ == "__main__":
    main()
