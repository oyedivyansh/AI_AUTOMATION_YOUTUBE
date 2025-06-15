import os
import io
import pickle
import time
import random
import schedule
from groq import Groq
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload

# --- CONFIG --- #
FOLDER_ID = "google drive folder id"  # ✅ Your Google Drive folder ID
LOCAL_FOLDER = "local path"  # ✅ Your local folder path


  # Google Drive folder ID

SCOPES = [
    "https://www.googleapis.com/auth/drive.readonly",
    "https://www.googleapis.com/auth/youtube.upload"
]
CREDENTIALS_FILE = "credentials.json"
TOKEN_FILE = "token.pickle"
DOWNLOAD_PATH = "latest_reel.mp4"
PROCESSED_FILE = "uploaded_ids.txt"

client = Groq(api_key="your groq api key")  # ✅ Your Groq API key


def authenticate_google():
    creds = None
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "rb") as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
        creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, "wb") as token:
            pickle.dump(creds, token)
    return creds
#if using Google Drive, uncomment the following function


# /*def get_latest_mp4_file(drive_service):
#     results = drive_service.files().list(
#         q=f"'{FOLDER_ID}' in parents",
#         orderBy="createdTime desc",
#         pageSize=10,
#         fields="files(id, name, mimeType, shortcutDetails)"
#     ).execute()
#     items = results.get("files", [])
#     if not items:
#         return None

#     uploaded_ids = []
#     if os.path.exists(PROCESSED_FILE):
#         with open(PROCESSED_FILE, "r") as f:
#             uploaded_ids = f.read().splitlines()

#     for item in items:
#         file_id = item["id"]
#         file_name = item["name"]
#         mime_type = item["mimeType"]

#         # If it's a shortcut
#         if mime_type == "application/vnd.google-apps.shortcut":
#             target_id = item.get("shortcutDetails", {}).get("targetId")
#             if not target_id or target_id in uploaded_ids:
#                 continue
#             # Get details of the actual file
#             real_file = drive_service.files().get(fileId=target_id, fields="id, name, mimeType").execute()
#             if real_file["mimeType"] != "video/mp4":
#                 continue
#             return real_file

#         # If it's a direct MP4 file
#         elif mime_type == "video/mp4" and file_id not in uploaded_ids:
#             return item

#     return None


#if using local folder, use the following function
def get_latest_mp4_file_from_local():
    if not os.path.exists(LOCAL_FOLDER):
        print("❌ Local folder does not exist.")
        return None

    uploaded_ids = []
    if os.path.exists(PROCESSED_FILE):
        with open(PROCESSED_FILE, "r") as f:
            uploaded_ids = f.read().splitlines()

    mp4_files = [
        f for f in os.listdir(LOCAL_FOLDER)
        if f.lower().endswith(".mp4") and f not in uploaded_ids
    ]

    if not mp4_files:
        return None

    # Sort by modified time, newest first
    mp4_files.sort(key=lambda x: os.path.getmtime(os.path.join(LOCAL_FOLDER, x)), reverse=True)
    return mp4_files[0]


def download_file(drive_service, file_id, file_name):
    request = drive_service.files().get_media(fileId=file_id)
    fh = io.FileIO(file_name, "wb")
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        status, done = downloader.next_chunk()
    return True



#title and description generation using Groq AI LLAMA model
def generate_title_description_randomly():
    # Step 1: Use Groq to get a basic idea
    prompt = (
        "Generate a short, catchy YouTube Shorts title and a casual/fun description for a tech-related funny video. "
        "Include some trendy or humorous tone, and use emojis. Keep it light-hearted. "
        "Do NOT include numbers, file names, or boring words. Avoid ending with punctuation."
    )

    response = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.9,
    )

    ai_response = response.choices[0].message.content.strip()
    
        # Parse response
    title, description = "", ""
    for line in ai_response.splitlines():
        if "title:" in line.lower():
            title = line.split(":", 1)[1].strip()
        elif "description:" in line.lower():
            description = line.split(":", 1)[1].strip()

    # Fallbacks in case Groq response is weird
    if not title:
        fallback_titles = [
            "AI Lost Its Mind Again 😵", 
            "When Robots Do Human Stuff 🤖", 
            "Tech Gone Wrong 💻🔥", 
            "ChatGPT Doing Nonsense", 
            "Coding in the Wild 🧠"
        ]
        title = random.choice(fallback_titles)

    if not description:
        fallback_desc = [
            "Bro this AI is losing it 😂 #shorts #tech",
            "POV: You gave AI caffeine ☕🤖 #shorts #funny",
            "Just your daily dose of chaos and code #shorts #automation",
            "When you let AI cook unsupervised 🍳👾 #shorts #ai",
            "You won’t believe what this bot just did 💀 #shorts #memes"
        ]
        description = random.choice(fallback_desc)

    # Step 2: Add random chaos hashtags/phrases
    suffixes = [
        "💀💻🔥", "🤯🤖", "🚀🚽", "😂😂", "😵‍💫💥", "👀", "💡", "👽", "🔍", "😎"
    ]
    extra_hashtags = [
        "#ai", "#memes", "#tech", "#funny", "#reels", "#coding", "#automation", "#wtf"
    ]

    # Finalize
    emojis = random.choice(suffixes)
    rand_tags = " ".join(random.sample(extra_hashtags, 2))

    final_description = f"{description} {emojis} #shorts {rand_tags}"

    return title, final_description



# Function to upload video to YouTube
def upload_to_youtube(youtube, title, description, file_path):
    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": [tag.replace("#", "") for tag in description.split() if "#" in tag],
            "categoryId": "28",  # Science & Technology
        },
        "status": {
            "privacyStatus": "public"
        }
    }

    media = MediaFileUpload(file_path, chunksize=-1, resumable=True, mimetype="video/*")
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
    response = request.execute()
    return response



# Function to mark a file as uploaded
def mark_as_uploaded(file_id):
    with open(PROCESSED_FILE, "a") as f:
        f.write(file_id + "\n")


# If using Google Drive, uncomment the following function
# def automate():
#     print("🔁 Running upload cycle...")
#     creds = authenticate_google()
#     drive_service = build("drive", "v3", credentials=creds)
#     youtube = build("youtube", "v3", credentials=creds)

#     file = get_latest_mp4_file(drive_service)
#     if not file:
#         print("✅ No new file to upload.")
#         return
#     print(f"📥 Downloading: {file['name']}")

#     print("📄 Generating title/description...")
#     title, description = generate_title_description_randomly()



#     print("📤 Uploading to YouTube...")
#     upload_response = upload_to_youtube(youtube, title.strip(), description, DOWNLOAD_PATH)
#     print(f"✅ Uploaded: https://www.youtube.com/watch?v={upload_response['id']}")
#     mark_as_uploaded(file["id"])


## Main automation function
def automate():
    print("🔁 Running upload cycle...")

    creds = authenticate_google()
    youtube = build("youtube", "v3", credentials=creds)

    latest_file = get_latest_mp4_file_from_local()
    if not latest_file:
        print("✅ No new video to upload from local folder.")
        return

    file_path = os.path.join(LOCAL_FOLDER, latest_file)
    print(f"📥 Found: {latest_file}")

    print("📄 Generating title/description...")
    title, description = generate_title_description_randomly()

    print("📤 Uploading to YouTube...")
    upload_response = upload_to_youtube(youtube, title.strip(), description, file_path)

    print(f"✅ Uploaded: https://www.youtube.com/watch?v={upload_response['id']}")
    mark_as_uploaded(latest_file)


print(f"📁 Using Google Drive folder: {FOLDER_ID}")


# Run once instantly
automate()

# Schedule to run every 4 hours
schedule.every(4).hours.do(automate)
ai_response = generate_title_description_randomly()
print("🕒 Scheduler started. Press Ctrl+C to stop.")
print("🔍 AI Response:\n", ai_response)

while True:
    schedule.run_pending()
    time.sleep(60)
