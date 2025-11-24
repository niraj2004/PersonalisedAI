from youtube_transcript_api import YouTubeTranscriptApi

print("Type:", type(YouTubeTranscriptApi))
print("Dir:", dir(YouTubeTranscriptApi))

try:
    print("Attempting to fetch transcript for a known video...")
    # Using a known working video ID (e.g., from a tutorial)
    transcript = YouTubeTranscriptApi.get_transcript("dQw4w9WgXcQ") # Rick Roll ID
    print("Success! First few chars:", str(transcript)[:100])
except Exception as e:
    print("Error:", e)
