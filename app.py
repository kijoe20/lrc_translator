import streamlit as st
import requests
import re

# Streamlit UI
st.title("LRC Lyrics Translator")
st.write("Upload an .lrc file, and get it translated to Japanese and Traditional Chinese.")

# Input fields for API key, Base URL, Model Name, and Translation Language
api_key = st.text_input("Enter your OpenAI-compatible API Key", type="password")
base_url = st.text_input("Enter your OpenAI-compatible API Base URL", value="https://api.openai.com")
model_name = st.text_input("Enter the Model Name", value="gpt-4o-mini")
translation_language = st.text_input("Enter the Desired Translation Language", value="Traditional Chinese")

# File uploader and text area for lyrics input
uploaded_file = st.file_uploader("Choose an .lrc file", type="lrc")
lyrics_text = st.text_area("Or, paste lyrics directly here")

# Button to start translation
if st.button("Start Translation"):
    # Check if we have either uploaded content or pasted text, and if API key, Base URL, Model Name, and Translation Language are provided
    if (uploaded_file or lyrics_text) and api_key and base_url and translation_language:
        # Get original content from file or text area
        if uploaded_file:
            original_content = uploaded_file.read().decode("utf-8")
        else:
            original_content = lyrics_text

        # Display original content (optional)
        st.subheader("Original Lyrics Content")
        st.text(original_content)

        # Translate the entire content using OpenAI-compatible API
        data = {
            "model": model_name,  # Use the user-provided model name
            "messages": [
                {"role": "system", "content": f"Translate the following .lrc lyrics to {translation_language}, make sure to provide in original followed by translated version, please output in .lrc table style."},
                {"role": "user", "content": original_content}
            ],
            "max_tokens": 2048  # Adjust max tokens as needed
        }
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        response = requests.post(f"{base_url}/v1/chat/completions", headers=headers, json=data)

        if response.status_code == 200:
            translated_content = response.json()["choices"][0]["message"]["content"].strip()
        else:
            translated_content = f"[Error: {response.status_code} - {response.text}]"

        # Display translated content
        st.subheader("Translated Lyrics Content")
        st.text(translated_content)

        # Provide download option for translated lyrics
        st.download_button(
            label="Download Translated .lrc",
            data=translated_content.encode("utf-8"),
            file_name="translated_lyrics.lrc",
            mime="text/plain"
        )
    else:
        st.warning("Please enter the API Key, Base URL, Model Name, and Translation Language to proceed.")