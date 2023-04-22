import io
import warnings
import streamlit as st
from datetime import date
import PIL
import os
from PIL import Image
import subprocess
from streamlit_image_select import image_select
import requests
from io import BytesIO
from stability_sdk import client
import stability_sdk.interfaces.gooseai.generation.generation_pb2 as generation

# App information
st.title("Meg\'s Cantonese Podcast Creator")
st.write(
    ":microphone: Upload an m4a audio file, generate a background image, and get a video with a waveform of the audio overlaid. [See the code](https://github.com/mrisdal/canto-podcast-creator) and check out my Instagram [Meg Learns Canto](https://www.instagram.com/meglearnscanto/)."
)

# Paths
audio_input_path = "./input/audio/"
background_input_path = "./input/backgrounds/"
waveform = audio_input_path + "waveform.mp4"
background_input = background_input_path + "background_4.jpg"

# Episode name
episode_name = "canto-{0}-video".format(date.today())

# File upload widget
audio_upload = st.file_uploader("The uploader expects an m4a file", type=["m4a"], label_visibility="collapsed")

# Generate a background image


with st.form("my_form"):
    # Explanation
    st.write("Enter a prompt. Otherwise press 'Submit' to use the placeholder prompt.")

    # Placeholder prompt
    placeholder = "A rabbit surrounded by red and blue flowers and gold filigree, ancient chinese art style"

    # Ask the user for a prompt
    prompt = st.text_input(label = "Enter a prompt or leave blank to use the placeholder prompt", value="", placeholder=placeholder, label_visibility="collapsed")

    # Get Stability AI token
    STABILITYAI_TOKEN = st.secrets["STABILITYAI_TOKEN"]

    # Our Host URL should not be prepended with "https" nor should it have a trailing slash.
    os.environ['STABILITY_HOST'] = 'grpc.stability.ai:443'
    os.environ['STABILITY_KEY'] = STABILITYAI_TOKEN

    # Set up our connection to the API
    stability_api = client.StabilityInference(
        key=os.environ['STABILITYAI_TOKEN'], # API Key reference.
        verbose=True, # Print debug messages.
        engine="stable-diffusion-xl-beta-v2-2-2", # Set the engine to use for generation.
        # Available engines: stable-diffusion-v1 stable-diffusion-v1-5 stable-diffusion-512-v2-0 stable-diffusion-768-v2-0
        # stable-diffusion-512-v2-1 stable-diffusion-768-v2-1 stable-diffusion-xl-beta-v2-2-2 stable-inpainting-v1-0 stable-inpainting-512-v2-0
    )

    # Every form must have a submit button.
    submitted = st.form_submit_button("Submit")
    # If a prompt is not entered when the form is submitted, just use the placeholder prompt
    if len(prompt)>0:
        prompt = prompt
    else:
        prompt = placeholder
    if submitted:
        # Set up our initial generation parameters
        answers = stability_api.generate(
            prompt=prompt,
            steps=30, # Amount of inference steps performed on image generation. Defaults to 30.
            cfg_scale=8.0, # Influences how strongly your generation is guided to match your prompt.
                        # Setting this value higher increases the strength in which it tries to match your prompt.
                        # Defaults to 7.0 if not specified.
            width=512, # Generation width, defaults to 512 if not included.
            height=512, # Generation height, defaults to 512 if not included.
            samples=1, # Number of images to generate, defaults to 1 if not included.
            sampler=generation.SAMPLER_K_DPMPP_2M # Choose which sampler we want to denoise our generation with.
                                                        # Defaults to k_dpmpp_2m if not specified. Clip Guidance only supports ancestral samplers.
                                                        # (Available Samplers: ddim, plms, k_euler, k_euler_ancestral, k_heun, k_dpm_2, k_dpm_2_ancestral, k_dpmpp_2s_ancestral, k_lms, k_dpmpp_2m, k_dpmpp_sde)
            #guidance_preset=generation.GUIDANCE_PRESET_FAST_GREEN # Enables CLIP Guidance.
        )

        # Set up our warning to print to the console if the adult content classifier is tripped.
        # If adult content classifier is not tripped, save generated images.
        for resp in answers:
            for artifact in resp.artifacts:
                if artifact.finish_reason == generation.FILTER:
                    warnings.warn(
                        "Your request activated the API's safety filters and could not be processed."
                        "Please modify the prompt and try again.")
                if artifact.type == generation.ARTIFACT_IMAGE:
                    sd_img = Image.open(io.BytesIO(artifact.binary))
                    sd_img.save("rabbit.png") # Save  generated image
                    #st.image(sd_img, caption=prompt)

# Function to download the uploaded audio file
def save_uploaded_audio(audio_file):
    # Read in the uploaded file
    with open(os.path.join(audio_input_path, "upload.m4a"),"wb") as f:
        f.write(audio_file.getbuffer())

# Function to process an audio file to add waveform to background image creating a video
def create_podcast(audio_upload):
    # Create waveform
    os.system(f'ffmpeg -i ./input/audio/{audio_upload} -filter_complex "[0:a]showwaves=s=512x200:mode=cline:colors=White@0.9|Black@0.75:draw=full:scale=sqrt,format=rgba[v]" -map "[v]" -map 0:a -c:v png -y {waveform}')
    
    # Put the waveform video on top of the selected background image
    os.system(f'ffmpeg -i rabbit.png -i {waveform} -filter_complex "[0:v][1:v] overlay=0:250" -pix_fmt yuv420p -c:a copy -y ./output/{episode_name}.mp4')
    
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

# Create podcast from the uploaded file
if audio_upload is not None:
    file_details = {"FileName":"upload.m4a","FileType":audio_upload.type}
    #st.write(file_details)
    save_uploaded_audio(audio_upload)
    create_podcast(audio_upload="upload.m4a")
else:
    create_podcast("./input/audio/test.m4a")
    #st.write("Upload an audio file to create a video")