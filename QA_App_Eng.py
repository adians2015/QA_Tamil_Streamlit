import streamlit as st
import pandas as pd
from gtts import gTTS
from io import BytesIO
import base64
import time

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="English Conversation Practice", layout="centered")
st.title("🗣 English Conversation Practice App")

# ---------------- LOAD DATA ----------------
df = pd.read_excel("conversation_data1.xlsx")
df.columns = df.columns.str.strip()  # clean column names

# ---------------- SESSION STATE ----------------
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

# ---------------- TOP CONTROLS ----------------
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

# ---------------- DELAY SLIDER ----------------
st.session_state.answer_delay = st.slider(
    "⏱ Answer speaking delay (seconds)",
    min_value=3,
    max_value=10,
    value=st.session_state.answer_delay,
    step=1
)

st.divider()

# ---------------- RESET ON TOPIC CHANGE ----------------
if st.session_state.current_topic != topic:
    st.session_state.index = 0
    st.session_state.current_topic = topic
    st.session_state.spoken_key = ""

if mode is not None:
    st.session_state.current_mode = mode

# ---------------- FILTER DATA ----------------
topic_df = (
    df[df["Topic"] == topic]
    .sort_values("Serial")
    .reset_index(drop=True)
)

row = topic_df.loc[st.session_state.index]

# ---------------- SAFE PRONOUNCE READER ----------------
def get_pronounce(column_name):
    value = row.get(column_name, "")
    if pd.isna(value):
        return ""
    return str(value).strip()

# ---------------- TEXT TO SPEECH (INDIAN ENGLISH) ----------------
def speak_js(text):
    if not text:
        return

    tts = gTTS(
        text=text,
        lang="en",       # ✅ English language
        tld="co.in",     # ✅ Indian English accent
        slow=False
    )

    audio_bytes = BytesIO()
    tts.write_to_fp(audio_bytes)
    audio_bytes.seek(0)
    b64_audio = base64.b64encode(audio_bytes.read()).decode()

    html = f"""
    <audio autoplay>
        <source src="data:audio/mp3;base64,{b64_audio}" type="audio/mp3">
    </audio>
    """
    st.components.v1.html(html, height=0, width=0)

# ---------------- DISPLAY ----------------
st.subheader(f"📝 {topic} – Question {row['Serial']}")

# -------- QUESTION --------
st.markdown("### ❓ Question")
st.info(row.get("Question", ""))
st.markdown(f"🗣 **Pronounce:** {get_pronounce('Question_Pronounce')}")
st.markdown(f"🌐 **Meaning:** {row.get('Question_Translation', '')}")

# -------- ANSWER --------
st.markdown("### ✅ Sample Answer")
st.success(row.get("Answer", ""))
st.markdown(f"🗣 **Pronounce:** {get_pronounce('Answer_Pronounce')}")
st.markdown(f"🌐 **Meaning:** {row.get('Answer_Translation', '')}")

# ---------------- AUTO SPEAK ----------------
current_key = f"{st.session_state.index}_{st.session_state.current_mode}"

if (
    st.session_state.current_mode is not None
    and st.session_state.spoken_key != current_key
):
    st.session_state.spoken_key = current_key

    if st.session_state.current_mode == "Ask Question":
        speak_js(get_pronounce("Question_Pronounce"))

    elif st.session_state.current_mode == "Answer Practice":
        time.sleep(st.session_state.answer_delay)
        speak_js(get_pronounce("Answer_Pronounce"))

st.divider()

# ---------------- NAVIGATION ----------------
c1, c2 = st.columns(2)

with c1:
    st.button("⬅ Previous", on_click=lambda: st.session_state.update(
        index=max(0, st.session_state.index - 1),
        spoken_key=""
    ))

with c2:
    st.button("Next ➡", on_click=lambda: st.session_state.update(
        index=min(len(topic_df) - 1, st.session_state.index + 1),
        spoken_key=""
    ))
