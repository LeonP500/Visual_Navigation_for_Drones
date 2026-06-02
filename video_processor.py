import cv2
import os
import pandas as pd
from srt_parser import parse_dji_srt

def process_video(video_path, srt_path, output_dir, frame_interval=30):
    """
    Extracts frames from the video and saves them to the output directory.
    Only extracts every `frame_interval` frame to save space (e.g., 30 = 1 fps).
    Returns a dataframe linking the saved image paths to the telemetry.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    print("Parsing SRT...")
    telemetry_df = parse_dji_srt(srt_path)
    
    print(f"Opening video: {video_path}")
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        print("Error: Could not open video.")
        return None

    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    print(f"Video FPS: {fps}, Total Frames: {total_frames}")

    saved_data = []
    
    frame_idx = 1 # SRT frames are 1-indexed usually
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        # Only process every Nth frame
        if frame_idx % frame_interval == 0:
            # Find the corresponding telemetry row
            # Telemetry frames are 1-indexed in our parser
            row = telemetry_df[telemetry_df['frame'] == frame_idx]
            
            if not row.empty:
                img_name = f"frame_{frame_idx:06d}.jpg"
                img_path = os.path.join(output_dir, img_name)
                
                # Resize the image to speed up future processing (e.g. 960x540)
                frame_resized = cv2.resize(frame, (960, 540))
                cv2.imwrite(img_path, frame_resized)
                
                # Record the data
                record = row.iloc[0].to_dict()
                record['image_path'] = img_path
                saved_data.append(record)
                
                if len(saved_data) % 10 == 0:
                    print(f"Extracted {len(saved_data)} keyframes... (current video frame {frame_idx}/{total_frames})")
                    
        frame_idx += 1

    cap.release()
    
    # Save the mapping
    db_df = pd.DataFrame(saved_data)
    db_csv_path = os.path.join(output_dir, "database.csv")
    db_df.to_csv(db_csv_path, index=False)
    print(f"Processing complete! Saved {len(db_df)} keyframes and database mapping to {db_csv_path}")
    
    return db_df

if __name__ == "__main__":
    video_file = "DJI_20260427152226_0017_D.MP4"
    srt_file = "DJI_20260427152226_0017_D.SRT"
    output_folder = "map_database"
    
    # Process 1 frame per second (assuming 30fps)
    process_video(video_file, srt_file, output_folder, frame_interval=30)
