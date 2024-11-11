import streamlit as st
import requests
import re

# Function to parse and translate the .lrc file
def parse_and_translate_lrc(content, api_key, base_url, target_languages=["Japanese", "Traditional Chinese"]):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    lines = content.decode("utf-8").splitlines()
    translated_lines = []

    for line in lines:
        # Check if line has timestamp
        match = re.match(r"^\[(\d{2}:\d{2}\.\d{2,3})\](.*)", line)
        if match:
            timestamp = match.group(1)
            text = match.group(2).strip()

            # Translate the text using OpenAI-compatible API
            translated_texts = []
            for lang in target_languages:
                data = {
                    "model": model_name,
                    "messages": [
                        {"role": "system", "content": f"Translate the following text to {lang}."},
                        {"role": "user", "content": text}
                    ],
                    "max_tokens": 60
                }
                response = requests.post(f"{base_url}/v1/chat/completions", headers=headers, json=data)
                
                if response.status_code == 200:
                    translated_text = response.json()["choices"][0]["message"]["content"].strip()
                    translated_texts.append(translated_text)
                else:
                    translated_texts.append(f"[Error: {response.status_code} - {response.text}]")

            # Append translated text in format with both languages
            translated_lines.append(f"[{timestamp}] " + " / ".join(translated_texts))
        else:
            # Handle lines without timestamps
            translated_lines.append(line)

    return "\n".join(translated_lines)

# Streamlit UI
st.title("LRC Lyrics Translator")
st.write("Upload an .lrc file, and get it translated to Japanese and Traditional Chinese.")

# Input fields for API key and Base URL
api_key = st.text_input("Enter your OpenAI-compatible API Key", type="password")
base_url = st.text_input("Enter your OpenAI-compatible API Base URL", value="https://api.openai.com")
model_name = st.text_input("Enter the Model Name", value="gpt-3.5-turbo")

# File uploader and text area for lyrics input
uploaded_file = st.file_uploader("Choose an .lrc file", type="lrc")
lyrics_text = st.text_area("Or, paste lyrics directly here")

# Button to start translation
if st.button("Start Translation"):
    # Check if we have either uploaded content or pasted text, and if API key, Base URL, and Model Name are provided
    if (uploaded_file or lyrics_text) and api_key and base_url:
        # Get original content from file or text area
        if uploaded_file:
            original_content = uploaded_file.read().decode("utf-8")
        else:
            original_content = lyrics_text

        # Display original content (optional)
        st.subheader("Original Lyrics Content")
        st.text(original_content)

        # Placeholder for incremental translation output
        translated_placeholder = st.empty()
        translated_content = []  # List to store the final translated content

        # Process and translate the content line by line
        lines = original_content.splitlines()
        for line in lines:
            # Check if line has timestamp
            match = re.match(r"^\[(\d{2}:\d{2}\.\d{2,3})\](.*)", line)
            if match:
                timestamp = match.group(1)
                text = match.group(2).strip()

                # Translate the text using OpenAI-compatible API
                translated_texts = []
                for lang in ["Japanese", "Traditional Chinese"]:
                    data = {
                        "model": model_name,  # Use the user-provided model name
                        "messages": [
                            {"role": "system", "content": f"Translate the following text to {lang}."},
                            {"role": "user", "content": text}
                        ],
                        "max_tokens": 256
                    }
                    headers = {
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json"
                    }
                    response = requests.post(f"{base_url}/v1/chat/completions", headers=headers, json=data)

                    if response.status_code == 200:
                        translated_text = response.json()["choices"][0]["message"]["content"].strip()
                        translated_texts.append(translated_text)
                    else:
                        translated_texts.append(f"[Error: {response.status_code} - {response.text}]")

                # Append translated text in format with both languages
                translated_line = f"[{timestamp}] " + " / ".join(translated_texts)
                translated_content.append(translated_line)

                # Update the placeholder with the new line
                translated_placeholder.text("\n".join(translated_content))

            else:
                # Handle lines without timestamps
                translated_content.append(line)
                translated_placeholder.text("\n".join(translated_content))

        # Provide download option for translated lyrics once all lines are processed
        st.download_button(
            label="Download Translated .lrc",
            data="\n".join(translated_content).encode("utf-8"),
            file_name="translated_lyrics.lrc",
            mime="text/plain"
        )
    else:
        st.warning("Please enter both the API Key, Base URL, and Model Name to proceed.")