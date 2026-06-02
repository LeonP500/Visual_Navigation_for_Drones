# Visual Navigation for Drones (GNSS-Denied)

This repository contains the implementation for the "Ex1 - Visual Navigation for Drones" assignment. The project focuses on determining a drone's position and the geographic coordinate it is looking at without the use of real-time GNSS data, by visually matching the live video feed against a pre-mapped flight database.

## Project Structure

*   `literature_review.md`: A literature review of recent state-of-the-art papers (2023-2024) with open-source code for cross-view and visual navigation.
*   `srt_parser.py`: A utility script to parse DJI's `.SRT` subtitle files to extract telemetry (Latitude, Longitude, Altitude).
*   `video_processor.py`: The preprocessing pipeline. It extracts keyframes from a reference video and links them to the extracted telemetry to build a visual map/database (`database.csv`).
*   `navigation.py`: The real-time navigation pipeline. It uses ORB feature extraction and Brute-Force matching (via OpenCV) to localize a new frame against the map. It then geometrically projects the drone's position to the ground coordinate using the drone's altitude and camera pitch angle (45 degrees).

## Prerequisites

This project is designed to be lightweight and easy to build. It requires Python 3.8+ and the following standard libraries:

```bash
pip install opencv-python pandas geopy matplotlib
```

## How to Run

### 1. Preprocessing (Map Building)
Place your DJI video (e.g., `DJI_20260427152226_0017_D.MP4`) and its corresponding telemetry subtitle file (`.SRT`) in the root directory. Run the preprocessor:

```bash
python video_processor.py
```
*This will create a `map_database` folder containing the keyframes and `database.csv`.*

### 2. Real-Time Navigation (Experiment)
Once the database is built, you can run the navigation pipeline. The script currently includes a preliminary experiment that analyzes a video, localizes the frames, computes the "look-at" coordinate, and generates a plotted trajectory comparing the visual estimation to the true SRT path.

```bash
python navigation.py
```
*This will output `preliminary_experiment.png` showing the tracked path.*

## Mathematical Approach

Since standard DJI SRT files do not include the Yaw (heading) angle, our `navigation.py` script automatically computes the drone's heading based on the derivative of consecutive GPS points from the map. The ground intersection is then calculated using standard trigonometric projection based on the relative altitude and the fixed camera depression angle.
