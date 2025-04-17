from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os
import pickle

# Set up the YouTube API client
client_secrets_file = 'YOUR_OAUTH_CLIENT_SECRETS_FILE.json'  # Replace with your OAuth client secrets file

def authenticate_oauth():
    credentials = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            credentials = pickle.load(token)

    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                client_secrets_file,
                scopes=['https://www.googleapis.com/auth/youtube.force-ssl']
            )
            credentials = flow.run_local_server(port=8080)

        with open('token.pickle', 'wb') as token:
            pickle.dump(credentials, token)

    return build('youtube', 'v3', credentials=credentials)


# Function to hide a comment instead of deleting it
def hide_comment(youtube, comment_id):
    try:
        youtube.comments().setModerationStatus(
            id=comment_id,
            moderationStatus="heldForReview"  # Hides the comment
        ).execute()
        print(f"Comment {comment_id} is now hidden (held for review).")
    except Exception as e:
        print(f"Error hiding comment {comment_id}: {e}")


# Main function
def main():
    # List of comment IDs to hide
    comment_ids = [
        'UgwqgR6_kfxzwx11LQp4AaABAg'
    ]

    youtube_authenticated = authenticate_oauth()

    # Loop through each comment ID and hide it
    for comment_id in comment_ids:
        hide_comment(youtube_authenticated, comment_id)  # Pass one ID at a time


if __name__ == '__main__':
    main()
