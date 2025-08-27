import streamlit as st
from pydub import AudioSegment
from pydub.silence import split_on_silence
import io, zipfile, time
from pathlib import Path
import tempfile

st.set_page_config(page_title="Silence Remover", page_icon="🎵", layout="wide")
st.title("🎵 Audio Silence Remover")

st.write("Upload audio file(s) and remove long silences automatically. The app will keep a **1 second gap** so speech stays natural.")

# Upload multiple files
uploaded_files = st.file_uploader("Upload audio files", type=["mp3", "wav", "ogg"], accept_multiple_files=True)

# Silence parameters (only tweak main detection, keep_silence fixed at 1000ms)
col1, col2 = st.columns(2)
with col1:
    min_silence_len = st.slider("Min silence length (ms)", 300, 3000, 700, 100)
with col2:
    silence_thresh = st.slider("Silence threshold (dB)", -60, 0, -40, 1)

processed_files = []

if uploaded_files:
    progress_bar = st.progress(0)
    total_files = len(uploaded_files)

    for idx, uploaded_file in enumerate(uploaded_files, start=1):
        with st.spinner(f"Processing {uploaded_file.name} ..."):
            st.subheader(f"🎧 {uploaded_file.name}")

            # Load audio
            audio = AudioSegment.from_file(uploaded_file)
            original_duration = len(audio) / 1000  # in seconds

            # Split audio on silence (force keep_silence = 1000ms)
            chunks = split_on_silence(
                audio,
                min_silence_len=min_silence_len,
                silence_thresh=silence_thresh,
                keep_silence=1000,
                seek_step=10
            )

            # Merge chunks
            processed_audio = AudioSegment.empty()
            for chunk in chunks:
                processed_audio += chunk
            processed_duration = len(processed_audio) / 1000

            # Save to memory buffer
            buf = io.BytesIO()
            processed_audio.export(buf, format="mp3")
            buf.seek(0)

            # Store for ZIP later
            file_name = f"{uploaded_file.name.rsplit('.',1)[0]}_processed.mp3"
            processed_files.append((file_name, buf.getvalue()))

            # Show processed audio only
            st.write(f"✅ Processed: {processed_duration:.2f} sec (saved {original_duration - processed_duration:.2f} sec)")
            st.audio(buf.getvalue(), format="audio/mp3")

            # Download processed file
            st.download_button(
                label=f"⬇️ Download {file_name}",
                data=buf.getvalue(),
                file_name=file_name,
                mime="audio/mp3"
            )
            st.markdown("---")

        # Update progress bar
        progress = int((idx / total_files) * 100)
        progress_bar.progress(progress)
        time.sleep(0.2)

    # ZIP download for all files
    if processed_files:
        zip_buf = io.BytesIO()
        with zipfile.ZipFile(zip_buf, "w") as zf:
            for fname, fdata in processed_files:
                zf.writestr(fname, fdata)
        zip_buf.seek(0)

        st.download_button(
            label="📦 Download All Processed Files (ZIP)",
            data=zip_buf,
            file_name="processed_audio_files.zip",
            mime="application/zip"
        )

    st.success("✅ All files processed!")

     # Notification sound and popup
    st.balloons()  # fun visual completion
    st.success("🎉 All files processed successfully!")
    
    # Play notification sound
    audio_file = Path(tempfile.gettempdir()) / "notify.mp3"
    if not audio_file.exists():
        # generate a simple beep
        from pydub.generators import Sine
        Sine(1000).to_audio_segment(duration=500).export(audio_file, format="mp3")
    audio_bytes = open(audio_file, "rb").read()
    st.audio(audio_bytes, format="audio/mp3")
