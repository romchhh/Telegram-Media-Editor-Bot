import asyncio
import os
from multiprocessing import Pool, cpu_count
from moviepy.editor import VideoFileClip
from functools import partial

from moviepy_video_handler import VideoProcessor

class SegmentsTooLongException(Exception):
    ...

def process_video_segment(segment_index, segment_start, segment_end, position, input_path, output_dir, quality="720p", 
    **kwargs):
    """Process a single segment of the video using VideoProcessor."""
    output_path = os.path.join(output_dir, f"segment_{segment_index}.mp4")
    video = VideoFileClip(input_path)
    processor = VideoProcessor(video)
    segment_clip = processor.video.subclip(segment_start, segment_end)
    
    segment_processor = VideoProcessor(segment_clip, quality=quality)
    
    segment_processor.process(output_path, position=position, **kwargs)
    segment_clip.close()
    processor.video.close()

    print(f"Segment {segment_index} processed and saved to {output_path}")
    return output_path

def divide_video_into_segments(input_path, num_segments, segment_duration=None):
    """Divide video into equal segments and return start and end times for each."""
    video = VideoFileClip(input_path)
    total_duration = video.duration
    
    if segment_duration is None:
        segment_duration = total_duration / num_segments
    
    if num_segments * segment_duration > total_duration:
        video.close()
        raise SegmentsTooLongException(f"Загальний час {num_segments} сегментів ({num_segments * segment_duration} секунд) більше довжини всього відео ({total_duration}). \nПоставте Довжину: Автоматично і ми порахуємо її самі)")
    
    segments = [(i, i * segment_duration, min((i + 1) * segment_duration, total_duration)) for i in range(num_segments)]
    video.close()
    return segments

def process_video_in_parallel(input_path, output_dir, position, num_segments=4, segment_duration=None, quality="720p", audio_tone_shift=0, 
    **kwargs):
    """Process video in parallel by dividing it into segments."""
    os.makedirs(output_dir, exist_ok=True)
    
    segments = divide_video_into_segments(input_path, num_segments, segment_duration)
    
    if segments is None:
        return
    
    with Pool(processes=min(num_segments, cpu_count())) as pool:
        process_segment_func = partial(process_video_segment, input_path=input_path, position=position,output_dir=output_dir, quality=quality, audio_tone_shift=audio_tone_shift, **kwargs)
        
        results = pool.starmap(process_segment_func, segments)
        
    print("All segments processed.")
    return results


if __name__ == "__main__":
    input_video_path = "main.mp4"
    output_directory = "segments"
    
    process_video_in_parallel(
        input_video_path, 
        output_directory, 
        position="top", 
        num_segments=1, 
        segment_duration=15,  
        footage_path="footage.mp4", 
        background_option="black",
        # background_video_path="back.mp4",
        quality="720p",
        audio_tone_shift=-0.5
    )
