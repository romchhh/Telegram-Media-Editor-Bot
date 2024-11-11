import asyncio
import os
from multiprocessing import Pool, cpu_count
from moviepy.editor import VideoFileClip
from functools import partial

from moviepy_video_handler import VideoProcessor

def process_video_segment(segment_index, segment_start, segment_end, input_path, output_dir, quality="720p",
    # user_id=None, callback_query=None, bot=None,
    **kwargs):
    """Process a single segment of the video using VideoProcessor."""
    output_path = os.path.join(output_dir, f"segment_{segment_index}.mp4")
    video = VideoFileClip(input_path)
    processor = VideoProcessor(video)
    segment_clip = processor.video.subclip(segment_start, segment_end)
    
    # Create a temporary processor for the segment
    segment_processor = VideoProcessor(segment_clip, quality=quality)
    
    # Process the segment with the same settings as the main video
    segment_processor.process(output_path, **kwargs)
    segment_clip.close()
    processor.video.close()

    # if user_id is not None:
    #     asyncio.run(send_segment(user_id, output_path, callback_query, bot))

    print(f"Segment {segment_index} processed and saved to {output_path}")
    return output_path

def divide_video_into_segments(input_path, num_segments, segment_duration=None):
    """Divide video into equal segments and return start and end times for each."""
    video = VideoFileClip(input_path)
    total_duration = video.duration
    
    # If no segment_duration is provided, divide the video into equal parts
    if segment_duration is None:
        segment_duration = total_duration / num_segments
    
    # Check if total duration is less than the total segment time (print message if not feasible)
    if num_segments * segment_duration > total_duration:
        video.close()
        print(f"Error: The total time for {num_segments} segments ({num_segments * segment_duration} seconds) exceeds the video duration ({total_duration} seconds).")
        return None
    
    segments = [(i, i * segment_duration, min((i + 1) * segment_duration, total_duration)) for i in range(num_segments)]
    video.close()
    return segments

def process_video_in_parallel(input_path, output_dir, num_segments=4, segment_duration=None, quality="720p",
    # user_id=None, callback_query=None, bot=None, 
    **kwargs):
    """Process video in parallel by dividing it into segments."""
    os.makedirs(output_dir, exist_ok=True)
    
    # Divide the video into segments
    segments = divide_video_into_segments(input_path, num_segments, segment_duration)
    
    # If the segments can't be divided correctly, return early
    if segments is None:
        return
    
    # Set up multiprocessing pool
    with Pool(processes=min(num_segments, cpu_count())) as pool:
        # Partial function with fixed parameters
        process_segment_func = partial(process_video_segment, input_path=input_path, output_dir=output_dir, quality=quality, **kwargs)
        
        # Unpack each segment tuple as arguments for process_video_segment
        results = pool.starmap(process_segment_func, segments)
        
    print("All segments processed.")
    return results

# async def send_segment(user_id, segment_path, callback_query, bot):
#     """Send a single video segment to the user."""
#     try:
#         with open(segment_path, 'rb') as video_file:
#             await bot.send_video(callback_query.message.chat.id, video_file, width=1080, height=1920)
#         print(f"Segment sent to user {user_id}: {segment_path}")
#     except Exception as e:
#         print(f"Error sending segment: {e}")

if __name__ == "__main__":
    input_video_path = "main.mp4"
    output_directory = "segments"
    
    process_video_in_parallel(
        input_video_path, 
        output_directory, 
        num_segments=8, 
        segment_duration=15,  
        footage_path="footage.mp4", 
        position="center", 
        background_option="video",
        background_video_path="back.mp4",
        quality="720p"
    )
