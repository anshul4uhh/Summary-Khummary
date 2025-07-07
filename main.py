import streamlit as st                            # For the web app UI
from youtube_transcript_api import YouTubeTranscriptApi  # To get video transcripts
import google.generativeai as genai               # To access Gemini API
import re
# To extract video ID from the URL

# ⛳ Configure your Gemini API key
import os
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")


def extract_video_id(url):
    match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11})", url)
    return match.group(1) if match else None

# def fetch_transcript(video_id):
#     try:
#         transcript = YouTubeTranscriptApi.fetch(video_id)
#         full_text = " ".join([entry['text'] for entry in transcript])
#         return full_text
#     except Exception as e:
#         return None

def fetch_transcript(video_id):
    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

        # Try manually created English or Hindi
        try:
            transcript = transcript_list.find_manually_created_transcript(['en', 'hi'])
        except:
            # Fallback to auto-generated transcripts
            transcript = transcript_list.find_generated_transcript(['en', 'hi'])

        # Fetch and build full text properly
        transcript_data = transcript.fetch()
        full_text = " ".join([entry.text for entry in transcript_data])  # ✅ FIXED here
        return full_text

    except Exception as e:
        print("❌ Transcript fetch error:", e)
        return None


def summarize_text_with_gemini(transcript):
    prompt = f"Summarize the following transcript in simple bullet points:\n\n{transcript}"
    response = model.generate_content(prompt)
    return response.text

st.set_page_config(page_title="Youtube Summarizer",layout="centered")
st.title("The Summary of Your Khummary")

# Sidebar – Enhanced
st.sidebar.title("🧭 App Flow")

st.sidebar.markdown("### 📺 YouTube Summarizer Steps:")
st.sidebar.markdown("""
1. Paste a valid **YouTube video URL**  
2. Click **Summarize**  
3. App will:
   - Extract transcript (English or Hindi)
   - Send it to **Gemini AI**
   - Generate a summary  
4. View the result instantly  
5. Download summary as:
   - 📄 TXT file
""")

st.sidebar.markdown("---")

st.sidebar.title("ℹ️ About")
st.sidebar.info(
    "This app uses YouTube transcripts and Google Gemini AI "
    "to provide short summaries of videos in simple bullet points."
)

st.sidebar.markdown("---")

st.sidebar.markdown("🧠 **Tip:** Best used with educational, explainer, or commentary videos.")

st.sidebar.markdown("---")

st.sidebar.markdown("👨‍💻 Made by [Anshul Shrivastava](https://www.linkedin.com/in/anshulshrivastavaa)")



yt_url = st.text_input("Enter youtube video url:")

if st.button("Summarize"):
    if not yt_url:
        st.warning("Please enter a youtube link.")
    else:
        with st.spinner("Fetching transcript and summarizing..."):
            video_id = extract_video_id(yt_url)
            if not video_id:
                st.error("Invalid YouTube link.")
            else:
                transcript = fetch_transcript(video_id)
                if not transcript:
                    st.error("Transcript not available for this video.")
                else:
                    summary = summarize_text_with_gemini(transcript)
                    st.subheader("📄 Summary")
                    st.markdown(summary)
                    summary_filename = "summary.txt"
                    with open(summary_filename, "w", encoding="utf-8") as f:
                        f.write(summary)

                    with open(summary_filename, "rb") as f:
                        st.download_button(
                            label="📥 Download Summary as .txt",
                            data=f,
                            file_name=summary_filename,
                            mime="text/plain"
                        )