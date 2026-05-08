import streamlit as st
from PIL import Image
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from msrest.authentication import CognitiveServicesCredentials
import azure.cognitiveservices.speech as speechsdk
import time

# -----------------------------
# Azure Credentials
# -----------------------------

VISION_KEY = "3rjI2tJgEjvUS9ve9DnwGTdgu0JW5B5i0u2mE8QpRzgaCPh4l1AwJQQJ99CEACYeBjFXJ3w3AAAFACOG0FxE"

VISION_ENDPOINT = "https://cv97898657.cognitiveservices.azure.com/"

SPEECH_KEY = "2LNcNfQUrK6f0jj3eZ1ssHm1qALaeiXmn1foajdEdGGo9bxH06i5JQQJ99CEACYeBjFXJ3w3AAAYACOGrjDr"

SPEECH_REGION = "eastus"

# -----------------------------
# Streamlit UI
# -----------------------------

st.title("📖 Readify AI")
st.subheader("Extract & Speak Text Instantly")

uploaded_file = st.file_uploader(
    "Upload an Image",
    type=["jpg", "jpeg", "png"]
)

# -----------------------------
# OCR Function
# -----------------------------

def extract_text(image_path):

    computervision_client = ComputerVisionClient(
        VISION_ENDPOINT,
        CognitiveServicesCredentials(VISION_KEY)
    )

    with open(image_path, "rb") as image_stream:

        read_response = computervision_client.read_in_stream(
            image_stream,
            raw=True
        )

    operation_location = read_response.headers["Operation-Location"]

    operation_id = operation_location.split("/")[-1]

    while True:

        read_result = computervision_client.get_read_result(operation_id)

        if read_result.status not in ['notStarted', 'running']:
            break

        time.sleep(1)

    extracted_text = ""

    if read_result.status == OperationStatusCodes.succeeded:

        for page in read_result.analyze_result.read_results:

            for line in page.lines:

                extracted_text += line.text + "\n"

    return extracted_text

# -----------------------------
# Text to Speech Function
# -----------------------------

def text_to_speech(text):

    speech_config = speechsdk.SpeechConfig(
        subscription=SPEECH_KEY,
        region=SPEECH_REGION
    )

    audio_config = speechsdk.audio.AudioOutputConfig(
        filename="output.wav"
    )

    synthesizer = speechsdk.SpeechSynthesizer(
        speech_config=speech_config,
        audio_config=audio_config
    )

    synthesizer.speak_text_async(text).get()

# -----------------------------
# Main App Logic
# -----------------------------

if uploaded_file is not None:

    image = Image.open(uploaded_file)

    st.image(image, caption="Uploaded Image", use_container_width=True)

    image_path = "temp_image.jpg"

    with open(image_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    with st.spinner("Extracting text..."):

        extracted_text = extract_text(image_path)

    st.success("Text Extracted Successfully!")

    st.text_area(
        "Extracted Text",
        extracted_text,
        height=200
    )

    if st.button("🔊 Convert to Speech"):

        text_to_speech(extracted_text)

        audio_file = open("output.wav", "rb")

        st.audio(audio_file.read())

        st.success("Speech Generated Successfully!")