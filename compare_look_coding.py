import numpy as np
import argparse

def get_sorted_look_starts(codingfile):
    f = open(codingfile, 'r')
    lines = f.readlines()[3:] # ignore header
    f.close()

    # Each line is in the format start, duration, type, mark\n
    codemarks = []
    for line in lines:
        pieces = line.strip().split(',')
        m = {'start': int(pieces[0]), 'duration': int(pieces[1]), 'type': pieces[2]}
        codemarks.append(m)
        
    # Sort by start time
    codemarks.sort(key=lambda m: m['start'])
    
    # Assume looking away until first coding mark
    real_codes = [code for code in codemarks if code["type"] in ["away", "left", "right"]]
    if real_codes[0]["start"] != 0:
        codemarks.insert(0, {"start": 0, "duration": 0, "type": "away"})
    
    # Cast out-of-frame looking to "away"
    additional_marks = []
    for code in codemarks:
        if code["type"] == "outofframe":
            start = code["start"]
            end = code["start"] + code["duration"]
            # Find the most recent non-outofframe mark before end of interval; plan to insert at end of interval
            before_end_marks = [code for code in codemarks if code["start"] < end and code["type"] in ["away", "left", "right"]]
            additional_marks.append({"start": end, "duration": 0, "type": before_end_marks[-1]["type"]})
            # Mark all coding within interval for deletion
            for code2 in codemarks:
                if start <= code2["start"] < end and code2["type"] in ["away", "left", "right"]:
                    code2["type"] = "delete"
            # Turn this one into an away mark
            code["type"] = "away"
            code["duration"] = 0
    codemarks = [code for code in codemarks if code["type"] in ["away", "left", "right"]] + additional_marks
    codemarks.sort(key=lambda m: m['start'])
            
    return codemarks
    
def get_total_time(codingfile):
    f = open(codingfile, 'r')
    lines = f.readlines()[3:] # ignore header
    f.close()

    # Each line is in the format start, duration, type, mark\n
    codemarks = []
    for line in lines:
        pieces = line.strip().split(',')
        m = {'start': int(pieces[0]), 'duration': int(pieces[1]), 'type': pieces[2]}
        codemarks.append(m)
        
    for code in codemarks:
        if code["type"] == "codingactive":
            return (code["start"], code["duration"] + code["start"])
    
def get_looking_array(codemarks, start_ms, end_ms):
    # Codemarks is sorted array of {"start": start_ms, "type": type} objects where 
    # type is "away", "left", or "right"
    looking_array = []
    
    type_codes = {"away": 1, "left": 2, "right": 3}
    
    # Find last mark before or at start (assume exists)
    before_start_marks = [code for code in codemarks if code["start"] <= start_ms]
    current_type = before_start_marks[-1]["type"]
    last_mark_ms = start_ms
    
    # Handle any marks within time range
    within_range_marks = [code for code in codemarks if start_ms < code["start"] < end_ms]
    for code in within_range_marks:
        looking_array += [type_codes[current_type]] * (int(code["start"]) - last_mark_ms)
        current_type = code["type"]
        last_mark_ms = int(code["start"])
    
    # Handle remaining time to end of range
    looking_array += [type_codes[current_type]] * (end_ms - last_mark_ms)
    return looking_array
    

def compare_look_coding(codingfile1, codingfile2):

    block_size = 1000
    
    # Assume coded time and lengths are the same - use first file to get period to focus on
    (start_time, end_time) = get_total_time(codingfile1)
    
    start_times = range(start_time, end_time, block_size)
    end_times = list(range(block_size + start_time, end_time, block_size)) + [end_time]
    
    marks1 = get_sorted_look_starts(codingfile1)
    marks2 = get_sorted_look_starts(codingfile2)
    
    agree_count = 0
    for (start, end) in zip(start_times, end_times):
        looks1 = np.asarray(get_looking_array(marks1, start, end))
        looks2 = np.asarray(get_looking_array(marks2, start, end))
        agree_count += np.sum(np.equal(looks1, looks2))
        
    total_time = end_time - start_time

    print(f"Total time coded: {total_time} ms")
    print(f"Agreement: {agree_count / total_time * 100 :.2f}%")
    
    return (agree_count / total_time, total_time)
    

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('file1', type=str, help='First coding file')
    parser.add_argument('file2', type=str, help='Second coding file to compare to first')
    opt = parser.parse_args()

    compare_look_coding(opt.file1, opt.file2)
