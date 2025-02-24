from flask import Flask, request, jsonify, send_from_directory, url_for
import yt_dlp
import os
import uuid
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

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
        unique_id = str(uuid.uuid4())[:8]
        filename_template = f"{DOWNLOAD_FOLDER}/%(title)s-{unique_id}.%(ext)s"

        # yt-dlp options (supports all sites)
        ydl_opts = {
            'outtmpl': filename_template,  # Save format
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best',  # Best video & audio
            'merge_output_format': 'mp4',  # Ensure MP4 output
            'postprocessors': [{'key': 'FFmpegMerger'}],  # Merge video & audio
            'cookiefile': 'cookies.txt' if os.path.exists('cookies.txt') else None,  # Use cookies if available
            'noplaylist': True  # Prevent downloading full playlists
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)

            # Extract the best available filename
            if 'requested_downloads' in info_dict:
                filename = info_dict['requested_downloads'][0]['filepath']
            else:
                filename = ydl.prepare_filename(info_dict)

        filename_only = os.path.basename(filename)
        download_url = url_for('get_video', filename=filename_only, _external=True)

        return jsonify({"message": "Download successful", "download_url": download_url})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/get_video/<filename>', methods=['GET'])
def get_video(filename):
    return send_from_directory(app.config['DOWNLOAD_FOLDER'], filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
