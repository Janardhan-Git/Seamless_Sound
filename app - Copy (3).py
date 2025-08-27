import streamlit as st
from pydub import AudioSegment
import numpy as np
import io, zipfile, time
from pathlib import Path
import tempfile
import base64

st.set_page_config(page_title="Silence Remover", page_icon="🎵", layout="wide")
st.title("🎵 Audio Silence Remover (Fast)")

st.write("Upload audio files and remove long silences automatically. A **1 second gap** is preserved between speech chunks.")

# Upload multiple files
uploaded_files = st.file_uploader("Upload audio files", type=["mp3", "wav", "ogg"], accept_multiple_files=True)

# Silence detection parameters
col1, col2 = st.columns(2)
with col1:
    frame_rate = st.slider("Resample audio for faster processing (Hz)", 8000, 44100, 16000, 1000)
with col2:
    silence_thresh = st.slider("Silence threshold (dB)", -60, 0, -40, 1)

processed_files = []

def remove_silence(audio_segment, silence_thresh=-40, min_silence_len=500, keep_silence=1000):
    """
    Remove silences from audio using NumPy for faster processing.
    Returns processed AudioSegment.
    """
    samples = np.array(audio_segment.get_array_of_samples())
    frame_rate = audio_segment.frame_rate
    # Convert dB threshold to amplitude
    thresh_amp = 10 ** (silence_thresh / 20) * np.max(np.abs(samples))
    
    # Compute frame-wise RMS
    chunk_ms = 10  # 10ms chunks
    chunk_len = int(frame_rate * chunk_ms / 1000)
    rms = []
    for i in range(0, len(samples), chunk_len):
        frame = samples[i:i+chunk_len]
        rms.append(np.sqrt(np.mean(frame**2)))
    rms = np.array(rms)
    
    # Detect non-silent chunks
    non_silent = np.where(rms > thresh_amp)[0]
    
    if len(non_silent) == 0:
        return AudioSegment.silent(duration=0)
    
    # Merge consecutive non-silent chunks
    chunks = []
    start_idx = non_silent[0]
    for i in range(1, len(non_silent)):
        if non_silent[i] != non_silent[i-1] + 1:
            start_ms = start_idx * chunk_ms
            end_ms = (non_silent[i-1]+1) * chunk_ms
            chunks.append(audio_segment[start_ms:end_ms])
            start_idx = non_silent[i]
    # last chunk
    start_ms = start_idx * chunk_ms
    end_ms = (non_silent[-1]+1) * chunk_ms
    chunks.append(audio_segment[start_ms:end_ms])
    
    # Merge chunks with keep_silence in between
    processed_audio = AudioSegment.empty()
    for chunk in chunks:
        processed_audio += chunk + AudioSegment.silent(duration=keep_silence)
    return processed_audio

if uploaded_files:
    progress_bar = st.progress(0)
    total_files = len(uploaded_files)

    for idx, uploaded_file in enumerate(uploaded_files, start=1):
        with st.spinner(f"Processing {uploaded_file.name} ..."):
            # Load and optionally resample
            audio = AudioSegment.from_file(uploaded_file)
            audio = audio.set_frame_rate(frame_rate)
            original_duration_min = len(audio) / 1000 / 60  # minutes

            # Remove silence
            processed_audio = remove_silence(audio, silence_thresh=silence_thresh, keep_silence=1000)
            processed_duration_min = len(processed_audio) / 1000 / 60  # minutes

            # Save to memory buffer
            buf = io.BytesIO()
            processed_audio.export(buf, format="mp3")
            buf.seek(0)

            file_name = f"{uploaded_file.name.rsplit('.',1)[0]}_processed.mp3"
            processed_files.append((file_name, buf.getvalue()))

            # Show processed audio
            st.write(f"✅ Processed: {processed_duration_min:.2f} min (saved {original_duration_min - processed_duration_min:.2f} min)")
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
