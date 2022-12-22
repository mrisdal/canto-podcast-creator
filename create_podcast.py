import streamlit as st
from datetime import date
import os

st.title("Meg\'s Cantonese Podcast Creator")
st.write(
    ":microphone: Upload an m4a audio file and get an image with a waveform of the audio overlaid. See the code: https://github.com/mrisdal/canto-podcast-creator"
)
st.sidebar.write("## Upload and download")

# Episode name
episode_name = "canto-{0}-video".format(date.today())

# File upload widget
audio_upload = st.sidebar.file_uploader("Upload an audio file", type=["m4a"])

# Paths
audio_input_path = "./input/audio/"
background_input_path = "./input/backgrounds/"
waveform = audio_input_path + "waveform.mp4"
background_input = background_input_path + "background_4.jpg"

# Function to download the uploaded audio file
def save_uploaded_audio(audio_file):
    # Read in the uploaded file
    with open(os.path.join(audio_input_path, "upload.m4a"),"wb") as f:
         f.write(audio_file.getbuffer())

# Function to process an audio file to add waveform to background image
def create_podcast(audio_upload):
    #st.write(audio_upload)
    os.system(f'ffmpeg -i ./input/audio/{audio_upload} -filter_complex "[0:a]showwaves=s=512x200:mode=cline:colors=White@0.9|Black@0.75:draw=full:scale=sqrt,format=rgba[v]" -map "[v]" -map 0:a -c:v png -y {waveform}')
    os.system(f'ffmpeg -i {background_input} -i {waveform} -filter_complex "[0:v][1:v] overlay=0:300" -pix_fmt yuv420p -c:a copy -y ./output/{episode_name}.mp4')
    podcast = open("./output/{}.mp4".format(episode_name), 'rb')
    podcast = podcast.read()
    st.video(podcast, format="video/mp4", start_time=0)
    st.sidebar.markdown("\n")
    with open("./output/{}.mp4".format(episode_name), 'rb') as file:
        btn = st.sidebar.download_button(
            label = "Download",
            data = file,
            file_name = "{}.mp4".format(episode_name),
            mime = "audio/x-m4a"
        )

# Create podcast from the uploaded file
if audio_upload is not None:
    file_details = {"FileName":"upload.m4a","FileType":audio_upload.type}
    #st.write(file_details)
    save_uploaded_audio(audio_upload)
    create_podcast(audio_upload="upload.m4a")
else:
    create_podcast("./input/audio/canto-2022-12-21-audio.m4a")