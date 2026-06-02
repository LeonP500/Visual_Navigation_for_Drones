import re
import pandas as pd

def parse_dji_srt(srt_path):
    """
    Parses a DJI SRT file and returns a pandas DataFrame with the telemetry data.
    """
    with open(srt_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Regular expressions to extract the data
    # Example format:
    # 1
    # 00:00:00,000 --> 00:00:00,033
    # <font size="28">FrameCnt: 1, DiffTime: 33ms
    # 2026-04-27 15:22:26.853
    # [iso: 100] [shutter: 1/1000.0] [fnum: 1.7] [ev: 0] [color_md: default] [focal_len: 24.00] [latitude: 32.102624] [longitude: 35.209724] [rel_alt: 19.600 abs_alt: 729.642] [ct: 5660] </font>
    
    blocks = content.strip().split('\n\n')
    
    data = []
    for block in blocks:
        lines = block.split('\n')
        if len(lines) < 5:
            continue
            
        frame_idx = int(lines[0].strip())
        time_str = lines[1].strip()
        
        # Extract metadata line
        meta_line = lines[4].strip()
        
        # Extract lat, lon, rel_alt, abs_alt using regex
        lat_match = re.search(r'\[latitude: ([-\d\.]+)\]', meta_line)
        lon_match = re.search(r'\[longitude: ([-\d\.]+)\]', meta_line)
        rel_alt_match = re.search(r'\[rel_alt: ([-\d\.]+)', meta_line)
        abs_alt_match = re.search(r'abs_alt: ([-\d\.]+)\]', meta_line)
        
        if lat_match and lon_match and rel_alt_match and abs_alt_match:
            data.append({
                'frame': frame_idx,
                'time': time_str,
                'latitude': float(lat_match.group(1)),
                'longitude': float(lon_match.group(1)),
                'rel_alt': float(rel_alt_match.group(1)),
                'abs_alt': float(abs_alt_match.group(1))
            })
            
    df = pd.DataFrame(data)
    return df

if __name__ == "__main__":
    # Test the parser
    srt_file = "DJI_20260427152226_0017_D.SRT"
    try:
        df = parse_dji_srt(srt_file)
        print(f"Successfully parsed {len(df)} frames from {srt_file}")
        print(df.head())
    except Exception as e:
        print(f"Error: {e}")
