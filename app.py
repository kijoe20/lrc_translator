import streamlit as st
import requests
import re

def translate_line_by_line(lines, api_key, base_url, model_name):
    translated_content = []
    for line in lines:
        match = re.match(r"^\[(\d{2}:\d{2}\.\d{2,3})\](.*)", line)
        if match:
            timestamp = match.group(1)
            text = match.group(2).strip()
            translated_texts = []
            for lang in ["Japanese", "Traditional Chinese"]:
                data = {
                      "messages": [

                        {"role": "system", "content": f"You are a highly skilled translator. Translate the following text to {lang}. Ensure the translation is accurate and maintains the original meaning."},

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
            translated_line = f"[{timestamp}] " + " / ".join(translated_texts)
            translated_content.append(translated_line)
        else:
            translated_content.append(line)
    return translated_content

def translate_whole_content(content, api_key, base_url, model_name, translation_language):
    data = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": f"Translate the following .lrc lyrics to {translation_language}, make sure to provide in original followed by translated version, please output in .lrc table style."},
            {"role": "user", "content": content}
        ],
        "max_tokens": 2048
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    response = requests.post(f"{base_url}/v1/chat/completions", headers=headers, json=data)
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"].strip()
    else:
        return f"[Error: {response.status_code} - {response.text}]"

#Streamlit configuration
st.set_page_config(
    page_title="LRC Lyrics Translator",
    page_icon="🎵", 
    layout="wide",
    initial_sidebar_state="expanded", # "auto", "expanded", or "collapsed"
)

with st.sidebar:
    st.markdown("## LRC Lyrics Translator")
    api_key = st.text_input("Enter your OpenAI-compatible API Key", type="password")
    base_url = st.text_input("Enter your OpenAI-compatible API Base URL", value="https://api.openai.com")
    model_name = st.text_input("Enter the Model Name", value="gpt-4o-mini")
    st.markdown("Created by [kijoe20](https://github.com/kijoe20)")

# Streamlit UI
st.title("LRC Lyrics Translator")
st.write("Upload an .lrc file, and get it translated.")

# Predefined list of languages
languages = ["English", "Japanese 日本語", "Traditional Chinese 繁體中文", "Simplified Chinese", "Spanish", "French", "German", "Other"]
selected_language = st.selectbox("Choose the Desired Translation Language", languages)

# Conditional text input for custom language
if selected_language == "Other":
    translation_language = st.text_input("Enter the Desired Translation Language")
else:
    translation_language = selected_language

uploaded_file = st.file_uploader("Choose an .lrc file", type="lrc")
lyrics_text = st.text_area("Or, paste lyrics directly here")

translation_mode = st.radio("Choose Translation Mode", ("Line by Line", "Whole Content"), help="Use the **Line by Line** if you need fine-grained control, better error handling for individual lines, or if the text is short enough that multiple API calls are not a concern. Use the **Whole Content** Method if you want to reduce the number of API calls, improve efficiency, and potentially get more consistent translations across the entire text.")

if st.button("Start Translation"):
    if (uploaded_file or lyrics_text) and api_key and base_url and model_name:
        if uploaded_file:
            original_content = uploaded_file.read().decode("utf-8")
        else:
            original_content = lyrics_text

        st.subheader("Original Lyrics Content")
        st.text(original_content)

        if translation_mode == "Line by Line":
            lines = original_content.splitlines()
            translated_content = translate_line_by_line(lines, api_key, base_url, model_name)
        else:
            translated_content = translate_whole_content(original_content, api_key, base_url, model_name, translation_language)

        st.subheader("Translated Lyrics Content")
        st.text("\n".join(translated_content))

        st.download_button(
            label="Download Translated .lrc",
            data="\n".join(translated_content).encode("utf-8"),
            file_name="translated_lyrics.lrc",
            mime="text/plain"
        )
    else:
        st.warning("Please enter the API Key, Base URL, and Model Name to proceed.")