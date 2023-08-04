import requests
from urllib.parse import quote
import pandas as pd
from datetime import datetime
import os

def get_steam_reviews(appid, language="english", filter="recent"):
    cursor = "*"
    previous_cursor = None
    reviews_data = []
    while cursor and cursor != previous_cursor:
        encoded_cursor = quote(cursor)
        url = f"https://store.steampowered.com/appreviews/{appid}?json=1&language={language}&cursor={encoded_cursor}&filter={filter}"
        response = requests.get(url)
        data = response.json()
        previous_cursor = cursor
        cursor = data.get("cursor")
        reviews = data["reviews"]
        for review in reviews:
            review_data = {
                "author": review["author"]["steamid"],
                "date": datetime.fromtimestamp(review["timestamp_created"]),
                "rating": "Positive" if review["voted_up"] else "Negative",
                "content": review["review"],
                "language": language,
                "playtime_forever": review['author']['playtime_forever'],
                'playtime_last_two_weeks': review['author']['playtime_last_two_weeks'],
                'playtime_at_review': review['author']['playtime_at_review'],
            }
            reviews_data.append(review_data)
    reviews_df = pd.DataFrame(reviews_data)
    desktop_path = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
    file_path = os.path.join(desktop_path, f"{appid}.xlsx")
    reviews_df.to_excel(file_path, sheet_name=appid, index=False)

appid = input("Wpisz ID gry: ")
get_steam_reviews(appid)
