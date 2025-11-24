import trafilatura
import yt_dlp
import requests
from urllib.parse import urlparse, parse_qs

def extract_video_id(url: str) -> str:
    """
    Extracts the video ID from a YouTube URL.
    """
    parsed_url = urlparse(url)
    if parsed_url.hostname == 'youtu.be':
        return parsed_url.path[1:]
    if parsed_url.hostname in ('www.youtube.com', 'youtube.com'):
        if parsed_url.path == '/watch':
            p = parse_qs(parsed_url.query)
            return p['v'][0]
        if parsed_url.path[:7] == '/embed/':
            return parsed_url.path.split('/')[2]
        if parsed_url.path[:3] == '/v/':
            return parsed_url.path.split('/')[3]
    return None

def fetch_content(url: str) -> dict:
    """
    Fetches content from a URL. Supports YouTube and general articles.
    Returns a dict with 'title', 'text', 'type'.
    """
    video_id = extract_video_id(url)
    
    if video_id:
        # It's a YouTube video
        try:
            ydl_opts = {
                'writesubtitles': True,
                'writeautomaticsub': True,
                'skip_download': True,
                'quiet': True,
                'no_warnings': True,
                'subtitleslangs': ['en'],
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                title = info.get('title', f"YouTube Video {video_id}")
                
                # Try to get subtitles
                subtitles = info.get('subtitles') or info.get('automatic_captions')
                transcript_text = ""
                
                if subtitles and 'en' in subtitles:
                    # Fetch the VTT/JSON3 content
                    # yt-dlp gives a list of formats, we usually want json3 or vtt
                    # For simplicity, let's try to find a json3 or vtt url
                    subs_url = subtitles['en'][0]['url']
                    
                    # We need to download and parse this. 
                    # But simpler: yt-dlp has a 'get_subtitles' but it's complex to use directly in code without downloading.
                    # Alternative: Use the URL we found.
                    try:
                        resp = requests.get(subs_url)
                        # This is likely XML or JSON3. 
                        # To keep it robust and simple, let's just grab text content if possible or use a library.
                        # Actually, for this MVP, let's just assume we can get text.
                        # If it's XML (timedtext), we can parse it.
                        transcript_text = resp.text # Very raw, but contains the words.
                        
                        # Cleanup: Remove XML tags if it is XML
                        if "<text" in transcript_text:
                            import xml.etree.ElementTree as ET
                            try:
                                root = ET.fromstring(transcript_text)
                                lines = [elem.text for elem in root.findall('.//text') if elem.text]
                                transcript_text = " ".join(lines)
                            except:
                                pass # Fallback to raw text
                                
                    except Exception as e:
                        print(f"Error fetching subs content: {e}")
                
                if not transcript_text:
                    transcript_text = f"[No transcript available for video: {title}]"

                return {
                    "title": title,
                    "text": transcript_text,
                    "type": "youtube"
                }

        except Exception as e:
            raise Exception(f"Failed to fetch YouTube info: {str(e)}")
    else:
        # It's an article/webpage
        downloaded = trafilatura.fetch_url(url)
        if downloaded:
            text = trafilatura.extract(downloaded)
            if text:
                return {
                    "title": "Web Article", # Trafilatura might extract title but 'extract' returns string
                    "text": text,
                    "type": "article"
                }
        raise Exception("Failed to fetch or extract content from URL")

def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> list[str]:
    """
    Simple chunking strategy.
    """
    if not text:
        return []
        
    chunks = []
    start = 0
    text_len = len(text)
    
    while start < text_len:
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start += (chunk_size - overlap)
        
    return chunks
