from flask import Flask, request, jsonify, send_from_directory, url_for
import yt_dlp
import os
import uuid
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Directory to store downloaded videos
DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)
app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER

# Function to merge video and audio using FFmpeg
def merge_video_audio(video_path, audio_path, output_path):
    os.system(f'ffmpeg -i "{video_path}" -i "{audio_path}" -c:v copy -c:a aac "{output_path}"')

@app.route('/download', methods=['POST'])
def download_video():
    data = request.json
    url = data.get('url')

    if not url:
        return jsonify({"error": "URL is required"}), 400

    try:
        unique_id = str(uuid.uuid4())[:8]  # Generate unique ID for filename
        video_path = f"{DOWNLOAD_FOLDER}/video-{unique_id}.mp4"
        audio_path = f"{DOWNLOAD_FOLDER}/audio-{unique_id}.m4a"
        output_path = f"{DOWNLOAD_FOLDER}/final-{unique_id}.mp4"

        # Download best video (without audio)
        with yt_dlp.YoutubeDL({'format': 'bestvideo[ext=mp4]', 'outtmpl': video_path}) as ydl:
            ydl.download([url])

        # Download best audio
        with yt_dlp.YoutubeDL({'format': 'bestaudio[ext=m4a]', 'outtmpl': audio_path}) as ydl:
            ydl.download([url])

        # Merge video and audio using FFmpeg
        merge_video_audio(video_path, audio_path, output_path)

        # Generate download URL
        filename_only = os.path.basename(output_path)
        download_url = url_for('get_video', filename=filename_only, _external=True)

        return jsonify({"message": "Download successful", "download_url": download_url})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/get_video/<filename>', methods=['GET'])
def get_video(filename):
    return send_from_directory(app.config['DOWNLOAD_FOLDER'], filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
