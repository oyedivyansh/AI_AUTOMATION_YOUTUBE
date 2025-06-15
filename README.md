# AI_AUTOMATION_YOUTUBE
Automates uploading YouTube Shorts from a local folder with random AI-generated titles, descriptions &amp; hashtags using Groq's LLaMA 3 API. Supports Google OAuth, scheduling, and avoids re-uploading the same videos. Just plug in your API &amp; run main.py! #YouTube #Automation #AI 

🎬 YouTube Shorts Uploader (AI Powered)

This Python project **automatically uploads YouTube Shorts** from your **local folder**. It uses **AI (Groq's LLaMA3)** to generate random, engaging titles, descriptions, and hashtags.

No more manual uploading! Just put your videos in a folder and run the script — it does the rest.

---

🔧 Features

- 📂 Scans local folder for `.mp4` videos
- 🧠 Uses **Groq AI** to generate titles + descriptions
- 📤 Uploads directly to your YouTube channel
- 🕒 Automatically runs every 4 hours (or manually)
- 🛑 Stops uploading already uploaded videos

---

🧠 How It Works

1. **Authenticate** with your Google (YouTube) account
2. **Scan** your local folder for the latest `.mp4` file
3. **Use Groq AI** to generate a catchy title + description
4. **Upload** the video to your YouTube channel
5. **Save video ID** so it never uploads the same one again

---

🗂 Folder Structure

├── main.py # Main script to run
├── credentials.json # Google API credentials
├── token.pickle # Auto-generated token after login
├── uploaded_ids.txt # Keeps track of uploaded videos
├── .env # Groq API key (optional)
└── latest_reel.mp4 # Temp downloaded video (auto)


---

## 🚀 Setup Guide

### 1. 🔑 Set up Google API
- Go to [Google Cloud Console](https://console.cloud.google.com/)
- Create OAuth client & enable:
  - YouTube Data API v3
  - Google Drive API (optional)
- Download `credentials.json` and place it in your project

### 2. 🔐 Get Groq API Key
- Go to [Groq Cloud](https://console.groq.com/)
- Copy your API key and paste into `.env` like this:


### 3. ▶️ Run it!
on bash
python main.py


### Finally 
The script will:

1..Ask you to sign in (only first time)

2..Start uploading automatically



