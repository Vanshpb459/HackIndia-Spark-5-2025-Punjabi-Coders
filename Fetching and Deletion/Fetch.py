import csv
import os
import datetime
from googleapiclient.discovery import build

# Set up the YouTube API client
api_key = 'AIzaSyBW8zzJFPTgLMvhVzB1TeiAbL-_g5egOYY'  # Replace with your actual API key
youtube = build('youtube', 'v3', developerKey=api_key)


# Function to fetch video IDs from a specific channel
def get_video_ids_from_channel(channel_id):
    video_ids = []
    next_page_token = None

    while True:
        # Fetch the videos from the channel
        request = youtube.search().list(
            part="snippet",
            channelId=channel_id,
            maxResults=50,  # Adjust number of results per page as needed
            pageToken=next_page_token
        )
        response = request.execute()

        # Extract video IDs
        for item in response.get('items', []):
            if item['id']['kind'] == 'youtube#video':  # Ensure the item is a video
                video_ids.append(item['id']['videoId'])

        # Check if there is another page of results
        next_page_token = response.get('nextPageToken')
        if not next_page_token:
            break

    return video_ids


# Function to generate a unique filename based on existing files
def generate_filename():
    # Get current date and time in the specified format
    now = datetime.datetime.now().strftime("%Y-%m-%d_%H.%M.%S")
    filename = f"allcommentsfetched_{now}.csv"
    return filename


# Function to fetch comments for multiple video IDs and save them to a CSV file
def fetch_comments_to_csv(video_ids):
    print(f"Fetching comments for video IDs: {video_ids}")

    # Generate a unique filename
    filename = generate_filename()

    # Open the CSV file in write mode
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(
            ['Video ID', 'Comment ID', 'Author', 'Comment', 'Published At', 'Author Channel'])  # Write header

        # Loop through each video ID
        for video_id in video_ids:
            print(f"Fetching comments for video ID: {video_id}")
            next_page_token = None  # Start with no page token

            while True:
                try:
                    # Fetch comments from the API
                    response = youtube.commentThreads().list(
                        part='snippet',
                        videoId=video_id,
                        textFormat='plainText',
                        maxResults=100,  # Fetch up to 100 comments per request
                        pageToken=next_page_token  # Fetch next page if available
                    ).execute()

                    # Handle comments and write them to CSV
                    if 'items' in response and response['items']:
                        for comment in response['items']:
                            top_comment = comment['snippet']['topLevelComment']['snippet']
                            author = top_comment['authorDisplayName']
                            text = top_comment['textDisplay']
                            published_at = top_comment['publishedAt']
                            author_channel = top_comment.get('authorChannelUrl', 'N/A')  # Handle missing author channel
                            comment_id = comment['id']  # Get the unique comment ID

                            # Write the data for each comment to the CSV file
                            writer.writerow([video_id, comment_id, author, text, published_at, author_channel])

                    else:
                        print(f"No comments found for video ID: {video_id}")
                        break  # No more comments, exit loop

                    # Check if there's another page of comments
                    next_page_token = response.get('nextPageToken')
                    if not next_page_token:
                        break  # No more pages, exit loop

                except Exception as e:
                    print(f"Error fetching comments for video ID {video_id}: {e}")
                    break  # Exit loop on error

    print(f"Comments have been saved to '{filename}'.")


# Main function
def main():
    # Replace with the desired YouTube channel ID
    channel_id = 'UC4V1nibieAtqDZWkPw9K8ew'  # Example channel ID
    video_ids = get_video_ids_from_channel(channel_id)

    # Call the function to fetch comments for all video IDs
    fetch_comments_to_csv(video_ids)


# Run the main function
if __name__ == '__main__':
    main()
