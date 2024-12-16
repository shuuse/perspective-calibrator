# Perspective Calibrator

An interactive tool for calibrating perspective transformation points, particularly useful for converting camera perspectives to birds-eye view. Originally developed for traffic analysis and vehicle speed estimation, but applicable to any perspective transformation needs.

## Features

- Interactive point selection interface
- Real-time preview of the transformed perspective
- Grid overlay for precise point placement
- Support for both image and video input
- Preview of the perspective transformation before finalizing
- Easy export of calibration points

## Installation

1. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

## Usage

1. Run the calibration tool:
```bash
python perspective_calibrator.py --input your_video.mp4
```

2. In the calibration window:
   - Click to place 4 points in order:
     1. Top left
     2. Top right
     3. Bottom right
     4. Bottom left
   - Press 'r' to reset points
   - Press 'c' to preview the transformation
   - Press 'q' to quit and save points

3. The tool will output the calibrated source points that can be used for perspective transformation.

## Example

```python
from perspective_calibrator import CalibrationTool

calibrator = CalibrationTool("path_to_video.mp4")
source_points = calibrator.calibrate()
print(f"Calibrated source points:\n{source_points}")
```

## Requirements

- Python 3.8+
- OpenCV (cv2) >= 4.8.0
- NumPy >= 1.24.0

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Acknowledgments

Originally developed for vehicle speed estimation from traffic camera footage, this tool has been generalized for wider use cases involving perspective transformation calibration.