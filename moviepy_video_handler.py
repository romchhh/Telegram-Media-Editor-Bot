import os
import cv2
from moviepy.editor import VideoFileClip, CompositeVideoClip
from moviepy.video.fx.resize import resize
from moviepy.video.fx.crop import crop
import numpy as np

class VideoProcessor:
    def __init__(self, input_path, target_width=1080, target_height=1920):

        self.input_path = input_path
        self.target_width = target_width
        self.target_height = target_height
        self.video = VideoFileClip(input_path)
        self.video_duration = self.video.duration

    def calculate_new_dimensions(self):
        target_ratio = self.target_width / self.target_height
        video_ratio = self.video.w / self.video.h

        if video_ratio > target_ratio:
            new_width = self.target_width
            new_height = int(new_width / video_ratio)
        else:
            new_height = self.target_height
            new_width = int(new_height * video_ratio)

        return new_width, new_height

    def create_background(self, option="black", background_video_path=None):
        match option:
            case "black":
                return (0, 0, 0)
            case "blurred":
                return self.create_blurred_background()
            case "video":
                if background_video_path:
                    background = self.create_video_background(background_video_path)
                    background.close()
                    return background
                else:
                    raise ValueError("No video provided for background")

    
    def create_blurred_background(self):
        low_res_video = resize(self.video, height=int(self.target_height / 2))
        
        def blur_frame(frame):
            frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            blurred_bgr = cv2.GaussianBlur(frame_bgr, (21, 21), sigmaX=10, sigmaY=10)
            return cv2.cvtColor(blurred_bgr, cv2.COLOR_BGR2RGB)
        
        blurred_video = low_res_video.fl_image(blur_frame)
        blurred_video = resize(blurred_video, height=self.target_height)

        if blurred_video.w > self.target_width:
            blurred_video = crop(blurred_video, width=self.target_width, height=self.target_height, x_center=blurred_video.w // 2, y_center=self.target_height // 2)
        return blurred_video
    
    def create_video_background(self, background_video_path):
        background_video = VideoFileClip(background_video_path).without_audio()

        if background_video.duration > self.video_duration:
            background_video = background_video.subclip(0, self.video_duration)
        else:
            background_video = background_video.loop(duration=self.video_duration)

        background_ratio = background_video.w / background_video.h
        target_ratio = self.target_width / self.target_height

        if background_ratio > target_ratio:
            new_width = self.target_width
            new_height = int(new_width / background_ratio)
        else:
            new_height = self.target_height
            new_width = int(new_height * background_ratio)

        background_video = resize(background_video, width=new_width, height=new_height)

        if new_width > self.target_width or new_height > self.target_height:
            background_video = crop(
                background_video, 
                width=self.target_width, 
                height=self.target_height, 
                x_center=new_width // 2, 
                y_center=new_height // 2
            )

        return background_video


    def resize_and_position_video(self, position="center", background_option="black", background_video_path=None):
        new_width, new_height = self.calculate_new_dimensions()
        resized_video = resize(self.video, width=new_width, height=new_height)
        background = self.create_background(option=background_option, background_video_path=background_video_path)

        if isinstance(background, tuple):
            final_video = resized_video.on_color(
                size=(self.target_width, self.target_height),
                color=background,
                pos=(position, "center") if position == "center" else (position, "top")
            )
        else:
            final_video = CompositeVideoClip([background, resized_video.set_position(("center", position))])
        # if background_video_path:
        #     background.close()
        return final_video

    def apply_greenscreen_effect(self, background_video, greenscreen_path):
        greenscreen = VideoFileClip(greenscreen_path)
        greenscreen_width = background_video.w
        greenscreen_height = int(greenscreen_width * (greenscreen.h / greenscreen.w))
        
        # Resize and loop greenscreen video to match background video duration
        greenscreen = greenscreen.resize(newsize=(greenscreen_width, greenscreen_height))
        greenscreen = greenscreen.subclip(0, self.video_duration) if greenscreen.duration > self.video_duration else greenscreen.loop(duration=self.video_duration)
        
        green_strip_height = background_video.h - greenscreen.h
        green_strip = np.full((green_strip_height, greenscreen_width, 3), fill_value=[0, 255, 0], dtype=np.uint8)

        def make_mask(frame):
            hsv_frame = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV)
            lower_green = np.array([35, 100, 100])
            upper_green = np.array([85, 255, 255])
            return cv2.inRange(hsv_frame, lower_green, upper_green) / 255

        def composite_frame(get_frame, t):
            frame_gs = greenscreen.get_frame(t)
            combined_frame = np.vstack((green_strip, frame_gs))
            
            mask = make_mask(combined_frame)
            
            bg_frame = background_video.get_frame(t)
            masked_bg = cv2.bitwise_and(bg_frame, bg_frame, mask=mask.astype(np.uint8))
            masked_gs = cv2.bitwise_and(combined_frame, combined_frame, mask=(1 - mask).astype(np.uint8))
            return cv2.add(masked_bg, masked_gs)

        
        return background_video.fl(composite_frame, apply_to='mask'), greenscreen

    def process(self, output_path, footage_path: None | str, position="center", background_option="blurred", background_video_path=None):
        final_video = self.resize_and_position_video(
            position=position, 
            background_option=background_option,
            background_video_path=background_video_path
            )

        if footage_path:
            final_video, greenscreen = self.apply_greenscreen_effect(final_video, footage_path)
            

        final_video.write_videofile(output_path, codec="libx264", threads=8, fps=30)
        final_video.close()
        if footage_path:
            greenscreen.close()


if __name__ == "__main__":
    input_video = "background.mp4"
    processor = VideoProcessor(input_video)

    # processor.process(
    #     "black_center.mp4", 
    #     "cal.mp4",
    #     position="center", 
    #     background_option="black"
    # )

    # processor.process(
    #     "blurred_top.mp4", 
    #     "papich2.mp4", 
    #     position="top", 
    #     background_option="blurred"
    # )

    # input_video = "input.mp4"
    # processor = VideoProcessor(input_video)
    # processor.process(
    #     "output.mp4",
    #     "papich2.mp4",
    #     position="top",
    #     background_option="video",
    #     backround_video_path="background1.mp4",
    # )

    input_video = "BAACAgIAAxkDAAIEJ2chJGGMqJUnXcye2kMVu4rTIuVgAAJJZgACi3YJSQHlBNjvOYKdNgQ.mp4"
    processor = VideoProcessor(input_video)
    processor.process(
        "long_output.mp4",
        footage_path=None,
        # "papich2.mp4",
        position="center",
        background_option="black",
        # background_video_path="background1.mp4",
    )

    # processor.process(
    #     "long_output.mp4",
    #     footage_path=None,
    #     # "papich2.mp4",
    #     position="top",
    #     background_option="video",
    #     background_video_path="background1.mp4",
    # )
    