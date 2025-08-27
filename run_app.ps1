# Activate the venv first
& .\venv\Scripts\Activate.ps1

# Run Streamlit app
Start-Process "streamlit" -ArgumentList "run", "app.py"

# Wait for a few seconds
Start-Sleep -Seconds 1

# Open in Chrome
#Start-Process "C:\Program Files\Google\Chrome\Application\chrome.exe" "http://localhost:8501"


#Start-Process "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" "http://localhost:8502"

streamlit run app.py --server.port 8502

