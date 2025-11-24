import yt_dlp
import json

def get_transcript_ytdlp(video_url):
    ydl_opts = {
        'writesubtitles': True,
        'writeautomaticsub': True,
        'skip_download': True,
        'quiet': True,
        'no_warnings': True,
        'subtitleslangs': ['en'],
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(video_url, download=False)
            print(f"Title: {info.get('title')}")
            
            # Check for subtitles
            subtitles = info.get('subtitles') or info.get('automatic_captions')
            if subtitles and 'en' in subtitles:
                subs_url = subtitles['en'][0]['url']
                print(f"Subtitle URL found: {subs_url[:50]}...")
                return True
            else:
                print("No English subtitles found.")
                return False
                
        except Exception as e:
            print(f"Error: {e}")
            return False

print("Testing yt-dlp...")
get_transcript_ytdlp("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
