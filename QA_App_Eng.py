import streamlit as st
import pandas as pd
from gtts import gTTS
from io import BytesIO
import base64
import time

st.set_page_config(page_title="English Conversation Practice", layout="centered")
st.title("🗣 English Conversation Practice App")

# Load Excel
df = pd.read_excel("conversation_data1.xlsx")

# ---------- SESSION STATE ----------
if "index" not in st.session_state:
    st.session_state.index = 0
if "current_topic" not in st.session_state:
    st.session_state.current_topic = None
if "current_mode" not in st.session_state:
    st.session_state.current_mode = None
if "spoken_key" not in st.session_state:
    st.session_state.spoken_key = ""
if "answer_delay" not in st.session_state:
    st.session_state.answer_delay = 5

# ---------- TOP CONTROLS ----------
col1, col2 = st.columns(2)

with col1:
    topic = st.selectbox("📌 Select Topic", df["Topic"].unique())

with col2:
    mode = st.radio(
        "🎯 Practice Mode",
        ["Ask Question", "Answer Practice"],
        index=None,
        horizontal=True
    )

# ---------- DELAY SLIDER ----------
st.session_state.answer_delay = st.slider(
    "⏱ Answer speaking delay (seconds)",
    min_value=3,
    max_value=10,
    value=st.session_state.answer_delay,
    step=1
)

st.divider()

# Reset index if topic changes
if st.session_state.current_topic != topic:
    st.session_state.index = 0
    st.session_state.current_topic = topic

# Update mode
if mode is not None:
    st.session_state.current_mode = mode

# Filter topic data
topic_df = df[df["Topic"] == topic].sort_values("Serial").reset_index(drop=True)

# ---------- CALLBACKS ----------
def next_question():
    if st.session_state.index < len(topic_df) - 1:
        st.session_state.index += 1

def prev_question():
    if st.session_state.index > 0:
        st.session_state.index -= 1

# ---------- DISPLAY ----------
row = topic_df.loc[st.session_state.index]

st.subheader(f"📝 {topic} – Question {row['Serial']}")

# -------- QUESTION --------
st.markdown("### ❓ Question")
st.info(row["Question"])
st.markdown(f"🗣 **Pronounce:** {row['Question_Pronounce']}")
st.markdown(f"🌐 **Meaning:** {row['Question_Translation']}")

# -------- ANSWER --------
st.markdown("### ✅ Sample Answer")
st.success(row["Answer"])
st.markdown(f"🗣 **Pronounce:** {row['Answer_Pronounce']}")
st.markdown(f"🌐 **Meaning:** {row['Answer_Translation']}")

# ---------- TEXT TO SPEECH ----------
def speak_js(text):
    tts = gTTS(text)
    audio_bytes = BytesIO()
    tts.write_to_fp(audio_bytes)
    audio_bytes.seek(0)
    b64_audio = base64.b64encode(audio_bytes.read()).decode()

    html_code = f"""
    <audio autoplay>
        <source src="data:audio/mp3;base64,{b64_audio}" type="audio/mp3">
    </audio>
    """
    st.components.v1.html(html_code, height=0, width=0)

# ---------- AUTO SPEAK ----------
current_key = f"{st.session_state.index}_{st.session_state.current_mode}"

if st.session_state.spoken_key != current_key and st.session_state.current_mode is not None:
    st.session_state.spoken_key = current_key

    if st.session_state.current_mode == "Ask Question":
        speak_js(row["Question"])

    elif st.session_state.current_mode == "Answer Practice":
        time.sleep(st.session_state.answer_delay)
        speak_js(row["Answer"])

st.divider()

# ---------- NAVIGATION ----------
c1, c2 = st.columns(2)
with c1:
    st.button("⬅ Previous", on_click=prev_question)
with c2:
    st.button("Next ➡", on_click=next_question)