from flask import Flask, request, jsonify
import yt_dlp
import os  # ✅ Fixed missing import
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def get_best_url(url):
    """Extracts the best available direct download URL using yt-dlp."""
    ydl_opts = {
        'format': 'bv*+ba/b[ext=mp4]/b',  # ✅ Best video + best audio, prefers MP4
        'noplaylist': True,  # ✅ Prevents downloading entire playlists
        'quiet': True,  # ✅ Hides unnecessary logs
        'nocheckcertificate': True,  # ✅ Fixes SSL issues
        'cookiefile': 'cookies.txt' if os.path.exists('cookies.txt') else None,  # ✅ Uses cookies if available
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)

            # ✅ Extract URL based on available fields
            if 'url' in info:
                return info['url']
            elif 'entries' in info and len(info['entries']) > 0:
                return info['entries'][0]['url']
        except Exception as e:
            return str(e)

    return None

@app.route('/download', methods=['POST'])
def download_video():
    data = request.json
    url = data.get('url')

    if not url:
        return jsonify({"error": "URL is required"}), 400

    direct_url = get_best_url(url)

    if not direct_url:
        return jsonify({"error": "Could not extract video URL"}), 500

    return jsonify({"message": "Success", "download_url": direct_url})

if __name__ == '__main__':
    app.run(debug=True)
