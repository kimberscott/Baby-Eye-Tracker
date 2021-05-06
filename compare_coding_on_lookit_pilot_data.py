import csv
from pathlib import Path
from compare_look_coding import raw_agreement
import subprocess as sp

# To use, download the following from https://osf.io/wbh7m/ into the same directory as 
# this script:
# 
# LookitPhysicsPilot_Participants.csv
# video/* 
# coding/ -> coding/human/

base_dir = Path(__file__).parent
video_path = base_dir / "video"
coding_path_in = base_dir / "coding" / "human"
coding_path_out = base_dir / "coding" / "iCatcher"

with open(Path(base_dir / 'LookitPhysicsPilot_Participants.csv'), newline='') as csvfile:
    reader = csv.DictReader(csvfile, delimiter=',')
    rows = [row for row in reader]
    
# Run iCatcher on each video listed in the CSV and save annotations
for iRow in range(len(rows)):
    row = rows[iRow]
    
    print(f'Processing video {row["VideoFilename"]}')
    
    input_video_path = video_path / row["VideoFilename"]
    output_video_path = video_path / "annotated" / row["VideoFilename"]
    output_annotation_path = coding_path_out / row["CodingFilename1"]
    
    if not output_annotation_path.is_file():
        print(f'\tAnnotation file not found, processing')
        sp.check_call([
            "python", 
            "example.py", 
            "--source_type", 
            "file", 
           input_video_path.resolve(),
            "--output_annotation", 
            output_annotation_path.resolve(),
            "--output_video_path", 
            output_video_path.resolve(),
        ])
        
# Compute agreement on each pair (human-iCatcher) of annotations

for iRow in range(len(rows)):
    row = rows[iRow]
    print(row["CodingFilename1"])
    (percent_agree, total_time, percent_agree_lr, total_time_lr) = raw_agreement(
        coding_path_in / row["CodingFilename1"], 
        coding_path_out / row["CodingFilename1"]
    )
    row["percent_agree"] = percent_agree
    row["percent_agree_lr"] = percent_agree_lr
    
# Save agreement stats to comparison CSV
    
with open('LookitPhysicsPilot_Participants_Comparison.csv', 'w', newline='') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)