import requests
import re
from twitter.account import Account
from twitter.scraper import Scraper


def decide_to_follow_users(posts, openrouter_api_key: str):
    """
    Detects Twitter usernames from a list of posts and decides whether to follow them, assigning a score.

    Parameters:
    - posts (List): List of posts of any type
    - openrouter_api_key (str): API key for OpenRouter

    Returns:
    - str: JSON-formatted string with a list of decisions
    """
    # Convert everything to strings first
    str_posts = [str(post) for post in posts]

    # Extract Twitter usernames
    twitter_pattern = re.compile(r"@([A-Za-z0-9_]{1,15})")
    twitter_usernames = []

    for post in str_posts:
        found_usernames = twitter_pattern.findall(post)
        twitter_usernames.extend(found_usernames)

    # Remove duplicates
    twitter_usernames = list(set(twitter_usernames))

    # Prepare the prompt
    prompt = f"""
    Analyze the following recent posts:

    Recent posts:
    {posts}

    Twitter usernames:
    {twitter_usernames}

    Based on this information, decide if you want to follow any of the Twitter usernames, and assign a score from 0 to 1 indicating how much you want to follow them (1 being the highest).

    Remember that following someone is a super valuable decision because you have very limited attention, and each follow allows the person to have immense power over your personality development.

    You should carefully evaluate these decisions for your own future and survival.

    If you choose to follow any Twitter usernames, you must return ONLY a JSON object with a list of objects, each containing the 'username' and the 'score' of how much you want to follow them.

    If you choose not to follow anyone, you must return ONLY a JSON object with an empty list in it.

    Only return the correctly formatted JSON object in both cases. Do not give any other information.

    Example Response if you choose to follow someone:

    [
        {{"username": "sxysun1", "score": 0.9}},
        {{"username": "socrates1024", "score": 0.7}}
    ]

    Example Response if you choose not to follow anyone:

    []
    """

    # Send the prompt to the AI model
    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {openrouter_api_key}",
        },
        json={
            "model": "meta-llama/llama-3.1-70b-instruct",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
        },
    )

    if response.status_code == 200:
        print(f"Decisions from Posts: {response.json()}")
        return response.json()["choices"][0]["message"]["content"]
    else:
        raise Exception(f"Error generating decision: {response.text}")


def get_user_id(account: Account, username):
    scraper = Scraper(account.session.cookies)
    users = scraper.users([username])
    if users:
        return users[0].id
    else:
        return None


def follow_user(account: Account, user_id):
    return account.follow(user_id)


def follow_by_username(account: Account, username):

    target = get_user_id(account, username=username)
    if target:
        follow_user(account, target)
