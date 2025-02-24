from flask import Flask, request, jsonify, send_from_directory, url_for
import yt_dlp
import os
import uuid
from flask_cors import CORS
import gunicorn

app = Flask(__name__)
CORS(app)

# Directory to store downloaded videos
DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)
app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER

@app.route('/download', methods=['POST'])
def download_video():
    data = request.json
    url = data.get('url')

    if not url:
        return jsonify({"error": "URL is required"}), 400

    try:
        # Generate a unique filename
        unique_id = str(uuid.uuid4())[:8]  # Generates a short unique identifier
        filename_template = f"{DOWNLOAD_FOLDER}/%(title)s-{unique_id}.%(ext)s"

        # Set yt-dlp options to download a single MP4 file
        ydl_opts = {
            'outtmpl': filename_template,
            'format': 'best[ext=mp4]/best',
            'postprocessors': []
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info_dict)

        # Extract filename from path
        filename_only = os.path.basename(filename)

        # Generate a unique downloadable URL
        download_url = url_for('get_video', filename=filename_only, _external=True)

        return jsonify({"message": "Download successful", "download_url": download_url})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/get_video/<filename>', methods=['GET'])
def get_video(filename):
    return send_from_directory(app.config['DOWNLOAD_FOLDER'], filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
