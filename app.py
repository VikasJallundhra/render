from flask import Flask, request, jsonify
import yt_dlp
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/download', methods=['POST'])
def get_download_url():
    data = request.json
    url = data.get('url')

    if not url:
        return jsonify({"error": "URL is required"}), 400

    try:
        ydl_opts = {
            'format': 'bv+ba/best',  # Best video + best audio
            'noplaylist': True,  # Prevent playlist downloads
            'cookiefile': 'cookies.txt' if os.path.exists('cookies.txt') else None,  # Use cookies if available
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)  # Don't download, just get info

            if 'url' in info_dict:
                video_url = info_dict['url']
            elif 'entries' in info_dict and len(info_dict['entries']) > 0:
                video_url = info_dict['entries'][0]['url']
            else:
                return jsonify({"error": "Could not extract video URL"}), 500

        return jsonify({"message": "Success", "download_url": video_url})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
