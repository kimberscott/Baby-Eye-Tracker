import numpy as np
import argparse

def get_sorted_look_starts(codingfile):
    with open(codingfile, 'r') as f:
        lines = f.readlines()[3:] # ignore header

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
    

def raw_agreement(coding_file_base, coding_file_comp):
    """ 
    Computes raw agreement (frames agreed / total frames coded) for two coding files.
    
    coding_file_base: path to "base" coding file (e.g., human coding) with "codingactive"
        event which will be used to determine which interval to use
    coding_file_comp: path to "comparison" coding file (e.g., iCatcher annotations)
    
    Returns: (agree_fraction, total_time, agree_fraction_lr, total_time_lr)
    
    agree_fraction: fraction of frames where coding files agree on label - right, left, or 
        away. Any 'outofframe' intervals are treated as 'away'.
    total_time: total duration of frames used, in ms
    
    agree_fraction_lr: fraction of frames where coding files agree on label right or left,
        restricted to frames where coding_file_base labels the file as left or right.
    total_time_lr: total duration of frames where coding_file_base labels the file as left
        or right
    """

    block_size = 1000
    
    # Assume coded time and lengths are the same across files - 
    # use first file to get period to focus on (based on "codingactive" mark)
    (start_time, end_time) = get_total_time(coding_file_base)
    
    start_times = range(start_time, end_time, block_size)
    end_times = list(range(block_size + start_time, end_time, block_size)) + [end_time]
    
    marks1 = get_sorted_look_starts(coding_file_base)
    marks2 = get_sorted_look_starts(coding_file_comp)
    
    agree_count = 0
    agree_count_lr = 0
    total_time_lr = 0
    for (start, end) in zip(start_times, end_times):
        looks1 = np.asarray(get_looking_array(marks1, start, end))
        looks2 = np.asarray(get_looking_array(marks2, start, end))
        agree_count += np.sum(np.equal(looks1, looks2))
        looks1_in_lr = looks1 != 1
        agree_count_lr += np.sum(np.equal(looks1[looks1_in_lr], looks2[looks1_in_lr]))
        total_time_lr += np.sum(looks1_in_lr)
        
    total_time = end_time - start_time
    
    return (agree_count / total_time, total_time, agree_count_lr / total_time_lr, total_time_lr)
    
# TODO: raw agreement, blocked by interval
# TODO: agreement, excluding periods close to transitions in coding_file_base
# TODO: looking time to left / (looking time to left or right), per interval, for each
    

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('file1', type=str, help='First coding file')
    parser.add_argument('file2', type=str, help='Second coding file to compare to first')
    opt = parser.parse_args()

    (agree_fraction, total_time) = raw_agreement(opt.file1, opt.file2)
    print(f"Total time coded: {total_time} ms")
    print(f"Agreement: {agree_fraction * 100 :.2f}%")
