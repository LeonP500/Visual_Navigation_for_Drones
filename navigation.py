import cv2
import pandas as pd
import numpy as np
from geopy.distance import distance
import math
import os
import matplotlib.pyplot as plt
from srt_parser import parse_dji_srt

class VisualNavigator:
    def __init__(self, db_csv_path):
        self.db = pd.read_csv(db_csv_path)
        self.orb = cv2.ORB_create()
        self.bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
        self.db_features = []
        
        print("Precomputing features for database...")
        for idx, row in self.db.iterrows():
            img_path = row['image_path']
            if os.path.exists(img_path):
                img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
                kp, des = self.orb.detectAndCompute(img, None)
                self.db_features.append({'kp': kp, 'des': des, 'row': row})
            else:
                self.db_features.append(None)
        print("Feature precomputation complete.")

    def compute_heading(self, row_idx):
        """Estimate heading from consecutive GPS points in the database"""
        if row_idx < len(self.db) - 1:
            p1 = self.db.iloc[row_idx]
            p2 = self.db.iloc[row_idx + 1]
        elif row_idx > 0:
            p1 = self.db.iloc[row_idx - 1]
            p2 = self.db.iloc[row_idx]
        else:
            return 0.0
            
        lat1, lon1 = math.radians(p1['latitude']), math.radians(p1['longitude'])
        lat2, lon2 = math.radians(p2['latitude']), math.radians(p2['longitude'])
        dlon = lon2 - lon1
        
        x = math.sin(dlon) * math.cos(lat2)
        y = math.cos(lat1) * math.sin(lat2) - (math.sin(lat1) * math.cos(lat2) * math.cos(dlon))
        
        initial_bearing = math.atan2(x, y)
        heading = math.degrees(initial_bearing)
        heading = (heading + 360) % 360
        return heading

    def localize(self, frame):
        """Find the most similar image in the database and return its telemetry"""
        frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        kp, des = self.orb.detectAndCompute(frame_gray, None)
        
        if des is None:
            return None
            
        best_match_idx = -1
        max_matches = 0
        
        for idx, db_feat in enumerate(self.db_features):
            if db_feat is None or db_feat['des'] is None: continue
            
            matches = self.bf.match(des, db_feat['des'])
            
            # Filter good matches using a distance threshold
            good_matches = [m for m in matches if m.distance < 50]
            
            if len(good_matches) > max_matches:
                max_matches = len(good_matches)
                best_match_idx = idx
                
        if best_match_idx != -1 and max_matches > 10:
            row = self.db_features[best_match_idx]['row']
            heading = self.compute_heading(best_match_idx)
            return {
                'latitude': row['latitude'],
                'longitude': row['longitude'],
                'rel_alt': row['rel_alt'],
                'heading': heading,
                'matches': max_matches
            }
        return None

def compute_look_at_coordinate(lat, lon, alt, heading, camera_angle_deg=45):
    """
    Computes the coordinate the camera is looking at on the ground.
    camera_angle_deg: depression angle (60 degrees).
    """
    # Distance on ground = Altitude / tan(angle)
    # math.tan expects radians
    angle_rad = math.radians(camera_angle_deg)
    distance_m = alt / math.tan(angle_rad)
    
    # Project coordinate
    start_point = (lat, lon)
    target_point = distance(meters=distance_m).destination(start_point, bearing=heading)
    
    return target_point.latitude, target_point.longitude

if __name__ == "__main__":
    db_csv = "map_database/database.csv"
    nav = VisualNavigator(db_csv)
    
    # Run preliminary experiment using a few frames from a video
    video_path = "DJI_20260427152226_0017_D.MP4"
    srt_path = video_path.replace(".MP4", ".SRT").replace(".mp4", ".srt")
    
    print(f"Parsing test SRT to get true path: {srt_path}...")
    test_telemetry_df = parse_dji_srt(srt_path)
    
    cap = cv2.VideoCapture(video_path)
    
    predicted_path = []
    true_path = []
    
    print("Running preliminary experiment (testing first 30 seconds)...")
    frame_idx = 1 # Start at 1 to align with srt frame indices
    while True:
        ret, frame = cap.read()
        if not ret or frame_idx > 30 * 30: # Test on first 900 frames
            break
            
        if frame_idx % 30 == 0: # Check 1 fps
            # Extract true coordinate for this frame from the video's SRT
            true_row = test_telemetry_df[test_telemetry_df['frame'] == frame_idx]
            if not true_row.empty:
                true_path.append((true_row.iloc[0]['latitude'], true_row.iloc[0]['longitude']))
                
            frame_resized = cv2.resize(frame, (960, 540))
            loc = nav.localize(frame_resized)
            if loc:
                predicted_path.append((loc['latitude'], loc['longitude']))
                target_lat, target_lon = compute_look_at_coordinate(
                    loc['latitude'], loc['longitude'], loc['rel_alt'], loc['heading']
                )
                print(f"Frame {frame_idx}: Localized at ({loc['latitude']:.5f}, {loc['longitude']:.5f}), Looking at ({target_lat:.5f}, {target_lon:.5f})")
                
        frame_idx += 1
        
    cap.release()
    
    # Plotting
    pred_lats = [p[0] for p in predicted_path]
    pred_lons = [p[1] for p in predicted_path]
    true_lats = [p[0] for p in true_path]
    true_lons = [p[1] for p in true_path]
    
    plt.figure(figsize=(10, 6))
    plt.plot(true_lons, true_lats, 'b-', label='True Path (SRT)')
    plt.plot(pred_lons, pred_lats, 'rx', label='Predicted Path (Visual)')
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.title('Preliminary Experiment: Visual Localization Path')
    plt.legend()
    plt.savefig('preliminary_experiment.png')
    print("Experiment complete. Saved plot to preliminary_experiment.png")
