import streamlit as st
from datetime import date
import os
import subprocess
from streamlit_image_select import image_select

# App information
st.title("Meg\'s Cantonese Podcast Creator")
st.write(
    ":microphone: Upload an m4a audio file, choose a background image, and get a video with a waveform of the audio overlaid. [See the code](https://github.com/mrisdal/canto-podcast-creator) and check out my Instagram [Meg Learns Canto](https://www.instagram.com/meglearnscanto/)."
)

# Paths
audio_input_path = "./input/audio/"
background_input_path = "./input/backgrounds/"
waveform = audio_input_path + "waveform.mp4"
background_input = background_input_path + "background_4.jpg"

# Episode name
episode_name = "canto-{0}-video".format(date.today())

# File upload widget
st.write("## Step 1. Upload an audio file")
audio_upload = st.file_uploader("The uploader expects an m4a file", type=["m4a"])

# Select a background image
st.write("## Step 2. Choose a background image")

backgrounds = []

for path in os.listdir(background_input_path):
    # Check if current path is a file and add it to a list
    # All the files here should be images. They don't need to be the same size, but ideally they're square
    if os.path.isfile(os.path.join(background_input_path, path)):
        backgrounds.append(background_input_path + path)

# Image selector widget
selected_image = image_select("Background choices", backgrounds)
st.write(selected_image)

# Get dimensions of the selected background image
selected_image_width = subprocess.run(f'ffprobe -v error -select_streams v:0 -show_entries stream=width -of csv=s=x:p=0 {selected_image}', stdout=subprocess.PIPE)
selected_image_width = selected_image_width.stdout.decode('utf-8').strip()

selected_image_height = subprocess.run(f'ffprobe -v error -select_streams v:0 -show_entries stream=height -of csv=s=x:p=0 {selected_image}', stdout=subprocess.PIPE)
selected_image_height = selected_image_height.stdout.decode('utf-8').strip()
#st.write(selected_image_width)

# Function to download the uploaded audio file
def save_uploaded_audio(audio_file):
    # Read in the uploaded file
    with open(os.path.join(audio_input_path, "upload.m4a"),"wb") as f:
         f.write(audio_file.getbuffer())

# Function to process an audio file to add waveform to background image creating a video
def create_podcast(audio_upload):
    # Create waveform
    os.system(f'ffmpeg -i ./input/audio/{audio_upload} -filter_complex "[0:a]showwaves=s={str(selected_image_width)}x{str(int(0.5 * int(selected_image_height)))}:mode=cline:colors=White@0.9|Black@0.75:draw=full:scale=sqrt,format=rgba[v]" -map "[v]" -map 0:a -c:v png -y {waveform}')
    
    # Put the waveform video on top of the selected background image
    os.system(f'ffmpeg -i {selected_image} -i {waveform} -filter_complex "[0:v][1:v] overlay=0:{str(int(0.5 * int(selected_image_height)))}" -pix_fmt yuv420p -c:a copy -y ./output/{episode_name}.mp4')
    
    # Display the video and make it available for download
    podcast = open("./output/{}.mp4".format(episode_name), 'rb')
    podcast = podcast.read()
    with open("./output/{}.mp4".format(episode_name), 'rb') as file:
        btn = st.download_button(
            label = "Download",
            data = file,
            file_name = "{}.mp4".format(episode_name),
            mime = "audio/x-m4a"
        )
    st.video(podcast, format="video/mp4", start_time=0)
    
st.write("## Step 3. View and download the result")

# Create podcast from the uploaded file
if audio_upload is not None:
    file_details = {"FileName":"upload.m4a","FileType":audio_upload.type}
    #st.write(file_details)
    save_uploaded_audio(audio_upload)
    create_podcast(audio_upload="upload.m4a")
else:
    create_podcast("./input/audio/canto-2022-12-21-audio.m4a")