# 🎵 Audio Silence Remover
Skip the gaps. Save time.

![Banner](assets/banner.png)

## 🚀 About
This Streamlit app lets you upload one or more audio files and automatically removes long silences/gaps.  
Perfect for cleaning up recordings, lectures, podcasts, or meetings!

## ✨ Features
- Upload **multiple audio files** at once
- Adjustable silence removal settings:
  - Minimum silence length (ms)
  - Silence threshold (dB)
  - Keep short silence around chunks
- Compare **original vs processed audio** side-by-side
- Download each processed file individually
- Download all processed files as a **ZIP**
- See time saved per file
- Progress bar + spinner during processing

## 🛠️ Tech Stack
- [Streamlit](https://streamlit.io/) - UI
- [pydub](https://github.com/jiaaro/pydub) - Audio processing
- [ffmpeg](https://ffmpeg.org/) - Audio backend

## 📦 Installation
```bash
git clone https://github.com/your-username/audio-silence-remover.git
cd audio-silence-remover
pip install -r requirements.txt
