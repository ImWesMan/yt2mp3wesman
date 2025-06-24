import tkinter as tk
from tkinter import filedialog, ttk
from pytubefix import YouTube
from pytubefix.cli import on_progress
import os
import re
import subprocess

def validate_youtube_url(url):
    """Check if the URL is a valid YouTube URL."""
    youtube_regex = (
        r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/'
        r'(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})'
    )
    return re.match(youtube_regex, url) is not None

def update_progress_bar(stream, chunk, bytes_remaining):
    """Update the progress bar based on download progress."""
    total_size = stream.filesize
    bytes_downloaded = total_size - bytes_remaining
    percentage = (bytes_downloaded / total_size) * 100
    progress_bar['value'] = percentage
    status_label.config(text=f"Downloading... {percentage:.1f}%")
    root.update()

def download_mp3():
    url = url_entry.get().strip()
    print(f"Starting download process for URL: {url}")
    status_label.config(text="Processing...", fg="blue")
    progress_bar['value'] = 0  # Reset progress bar

    # Validate URL
    if not url:
        status_label.config(text="Error: Please enter a URL", fg="red")
        print("Error: No URL provided")
        return
    if not validate_youtube_url(url):
        status_label.config(text="Error: Invalid YouTube URL", fg="red")
        print("Error: Invalid YouTube URL")
        return

    # Open file explorer to choose save directory
    save_dir = filedialog.askdirectory(title="Select Save Location")
    if not save_dir:
        status_label.config(text="Error: No save location selected", fg="red")
        print("Error: No save location selected")
        return

    try:
        # Download audio stream from YouTube
        print("Initializing YouTube object...")
        yt = YouTube(url, on_progress_callback=update_progress_bar, use_oauth=False, allow_oauth_cache=True)
        print(f"YouTube object created successfully. Title: {yt.title}")

        # Check video availability
        print("Checking video availability...")
        if yt.age_restricted:
            status_label.config(text="Error: Video is age-restricted", fg="red")
            print("Error: Video is age-restricted")
            return

        # Get audio stream
        print("Filtering for audio stream...")
        stream = yt.streams.filter(only_audio=True).first()
        if not stream:
            status_label.config(text="Error: No audio stream available", fg="red")
            print("Error: No audio stream available")
            return

        # Download to selected directory
        print(f"Downloading audio to {save_dir}...")
        out_file = stream.download(output_path=save_dir)
        print(f"Download completed: {out_file}")

        # Convert to MP3
        print("Converting to MP3 with ffmpeg...")
        base, ext = os.path.splitext(out_file)
        mp3_file = base + ".mp3"

        ffmpeg_path = os.path.join(os.path.dirname(__file__), "ffmpeg.exe")
        ffmpeg_cmd = [
            ffmpeg_path, "-y", "-i", out_file,
            "-vn", "-ab", "192k", "-ar", "44100", "-f", "mp3", mp3_file
        ]

        result = subprocess.run(ffmpeg_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)

        if result.returncode != 0:
            print("ffmpeg failed:", result.stderr)
            status_label.config(text=f"Error: ffmpeg conversion failed", fg="red")
            return

        print(f"MP3 conversion completed: {mp3_file}")

        # Delete original file
        print("Deleting original file...")
        os.remove(out_file)
        print("Original file deleted")

        status_label.config(text=f"Download complete! Saved as {os.path.basename(mp3_file)}", fg="green")
        print("Download process completed successfully")
    except Exception as e:
        status_label.config(text=f"Error: {str(e)}", fg="red")
        print(f"Error occurred: {str(e)}")

# GUI
root = tk.Tk()
root.title("YouTube to MP3 Downloader")
root.geometry("400x250") 

tk.Label(root, text="Paste YouTube URL:").pack(pady=5)
url_entry = tk.Entry(root, width=50)
url_entry.pack(pady=5)

tk.Button(root, text="Download MP3", command=download_mp3).pack(pady=10)
progress_bar = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate")
progress_bar.pack(pady=5)
status_label = tk.Label(root, text="", fg="black", wraplength=350)
status_label.pack(pady=5)

root.mainloop()