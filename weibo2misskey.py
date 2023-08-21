import json
import os
import time
import random
import logging
import requests
import weibo
import validators
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

CONFIG_FILE = 'config.json'

### Logging
logger = logging.getLogger('weibo2misskey')

### Misskey

def post_to_misskey(text, media_ids, config):
    """Post the given text and media to the provided Misskey instance."""
    misskey_instance_url = config['misskey_instance_url']
    misskey_token = config['misskey_token']

    payload = {
        "i": misskey_token,
        "text": text,
        "mediaIds": media_ids
    }

    response = requests.post(f"{misskey_instance_url}/api/notes/create", json=payload)
    return response.json()

def upload_media_to_misskey(media, config):
    """Upload media to Misskey and return the media ID."""
    misskey_instance_url = config['misskey_instance_url']
    misskey_token = config['misskey_token']

    files = {"file": media}
    data = {"i": misskey_token}

    response = requests.post(f"{misskey_instance_url}/api/drive/files/create", data=data, files=files)
    response_json = response.json()

    if 'id' not in response_json:
        print("Failed to upload media. Misskey response:", response_json)
        return None
    
    return response_json["id"]



def already_posted(post_id, file_path='posted_ids.txt'):
    """Check if a post ID is already in the file."""
    if not os.path.exists(file_path):
        with open(file_path, 'w'): pass  # Create the file if it doesn't exist

    with open(file_path, 'r') as file:
        return str(post_id) in file.read()


def mark_as_posted(post_id, file_path='posted_ids.txt'):
    """Mark a post ID as posted by adding it to the file."""
    with open(file_path, 'a') as file:
        file.write(str(post_id) + '\n')

def process_post_and_crosspost(post, config):
    post_id = post['id']
    if already_posted(post_id):
        logger.info(f"Post {post_id} has already been posted. Skipping...")
        return

    user_id = post['user_id']
    user_comment = next((user['comment'] for user in config['user_list'] if user['id'] == user_id), None)
    tag = f"#{user_comment}" if user_comment else ""

    text = f"{tag} {post['text']}"
    # Upload media if any.
    media_urls = []
    if post.get('pics'):
        media_urls.extend(post['pics'].split(','))
    if post.get('video_url'):
        media_urls.extend(post['video_url'].split(';'))

    # Setting up retry mechanism for requests
    session = requests.Session()
    retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
    session.mount('http://', HTTPAdapter(max_retries=retries))
    session.mount('https://', HTTPAdapter(max_retries=retries))

    media_ids = []
    for media_url in media_urls:
        if validators.url(media_url):
            try:
                response = session.get(media_url, timeout=10)  # using session with retries instead of just requests
                media_content = response.content
                media_id = upload_media_to_misskey(media_content, config)
                media_ids.append(media_id)
            except requests.RequestException as e:  # this captures all requests-related exceptions
                logger.error(f"Failed to download media from URL {media_url}. Error: {e}")

    post_to_misskey(text, media_ids, config)
    logger.info(f"Crossposted from Weibo user {post['screen_name']}.")

    # After successfully posting to Misskey:
    mark_as_posted(post_id)



def main():
    # Load config
    with open(CONFIG_FILE, 'r') as f:
        config = json.load(f)
    
    while True:
        logger.info("Fetching latest Weibo posts...")
        
        wb = weibo.Weibo(config)
        for user in wb.user_config_list:
            wb.initialize_info(user)
            wb.get_user_info()
            wb.get_one_page(1)

            for post in reversed(wb.weibo):
                process_post_and_crosspost(post, config)

        sleep_time = 20 * 60
        logger.info(f"Sleeping for {sleep_time//60} minutes...")
        time.sleep(sleep_time)

if __name__ == "__main__":
    main()
