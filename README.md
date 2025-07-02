# Vision-Bot

An automatic monster detection system that captures and analyzes screenshots every 10 seconds.

## Features

- **Automatic detection** of monsters on screen
- **Automatic screenshots** every 10 seconds
- **Save** images with detected monsters highlighted
- **Multiple templates** for different viewing angles
- **Real-time statistics**

## Structure

```
Vision-Bot/
├── main.py           # Main script
├── vision.py         # Image detection class
├── capture.py        # Screen capture
├── templates/        # Reference images
│   └── rat_1/        # Rat templates
└── screenshots/      # Captured images
```

## Usage

```bash
python main.py
```

The system will:
1. Initialize screen capture
2. Load monster templates
3. Take screenshots every 10 seconds
4. Detect and highlight found monsters
5. Save images in `screenshots/`

## Configuration

- **Detection threshold**: 0.70 (modifiable in `MONSTER_SYSTEM`)
- **Interval**: 10 seconds between captures
- **Templates**: Place your reference images in `templates/`

## Stop

Press `Ctrl+C` to stop the system.

## Results

Screenshots are saved with these names:
- `detection_YYYYMMDD_HHMMSS_Xmonsters.png` - with detections
- `screenshot_YYYYMMDD_HHMMSS_no_detections.png` - without detections

---
Developed by Doub (doub.cpp)
