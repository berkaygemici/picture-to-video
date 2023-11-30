import tkinter as tk
from tkinter import filedialog
from moviepy.editor import ImageClip, concatenate_videoclips
from moviepy.video.fx.all import crop
from PIL import Image
import os

class VideoEditorApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Video Editor App")

        self.clips = []
        self.duration_entry_var = tk.StringVar()
        self.duration_entry_var.set("2")  # Default duration

        # Create UI elements
        self.file_listbox = tk.Listbox(self.master, selectmode=tk.MULTIPLE)
        self.file_listbox.pack(pady=10)

        self.add_button = tk.Button(self.master, text="Add Images", command=self.add_images)
        self.add_button.pack()

        self.duration_label = tk.Label(self.master, text="Duration per clip (seconds):")
        self.duration_label.pack()

        self.duration_entry = tk.Entry(self.master, textvariable=self.duration_entry_var)
        self.duration_entry.pack()

        self.done_button = tk.Button(self.master, text="Done", command=self.process_images)
        self.done_button.pack()

    def add_images(self):
        file_paths = filedialog.askopenfilenames(title="Select Image Files", filetypes=[("Image files", "*.jpg;*.png")])
        for file_path in file_paths:
            self.file_listbox.insert(tk.END, file_path)

    def resize_and_crop(self, image_path, output_path, target_resolution=(1920, 1080)):
        # Open the image file
        img = Image.open(image_path)

        # Calculate the aspect ratio of the target resolution
        target_aspect_ratio = target_resolution[0] / target_resolution[1]

        # Get the aspect ratio of the original image
        original_aspect_ratio = img.width / img.height

        # Calculate the new size and position for the image
        if original_aspect_ratio > target_aspect_ratio:
            # Original image is wider, crop the sides
            new_width = int(img.height * target_aspect_ratio)
            left_margin = (img.width - new_width) // 2
            img = img.crop((left_margin, 0, left_margin + new_width, img.height))
        else:
            # Original image is taller, crop the top and bottom
            new_height = int(img.width / target_aspect_ratio)
            top_margin = (img.height - new_height) // 2
            img = img.crop((0, top_margin, img.width, top_margin + new_height))

        # Resize the image to the target resolution
        img = img.resize(target_resolution, Image.ANTIALIAS)

        # Save the result
        img.save(output_path)

    def resize_and_crop_all(self, input_paths, output_paths):
        for input_path, output_path in zip(input_paths, output_paths):
            self.resize_and_crop(input_path, output_path)

    def process_images(self):
        # Clear existing clips
        self.clips = []

        # Create a list to store paths of resized images
        resized_image_paths = []

        # Iterate through selected file paths
        for file_path in self.file_listbox.get(0, tk.END):
            resized_image_path = "resized_" + file_path.split("/")[-1]  # Modify this as needed
            resized_image_paths.append(resized_image_path)
            self.resize_and_crop(file_path, resized_image_path)

        # Resize and crop all images
        self.resize_and_crop_all(self.file_listbox.get(0, tk.END), resized_image_paths)

        # Iterate through resized image paths
        for resized_image_path in resized_image_paths:
            clip = ImageClip(resized_image_path).set_duration(float(self.duration_entry_var.get()))  # Use user-specified duration
            self.clips.append(clip)

        # Concatenate clips
        video_clip = concatenate_videoclips(self.clips, method='compose')

        # Save video file
        video_clip.write_videofile("video-output.mp4", fps=24, remove_temp=True, codec="libx264", audio_codec='aac')

        # Remove resized images
        for resized_image_path in resized_image_paths:
            os.remove(resized_image_path)

        # Display a message or perform any other post-processing steps if needed
        print("Video editing is complete.")

if __name__ == "__main__":
    root = tk.Tk()
    app = VideoEditorApp(root)
    root.mainloop()