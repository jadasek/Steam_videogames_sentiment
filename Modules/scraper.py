import requests
from urllib.parse import quote
import pandas as pd
from datetime import datetime
from tkinter import ttk
import os
import time

def get_steam_reviews(file_path, callback, total, appid, language, amount=100, filter="recent"):
    cursor = "*"
    previous_cursor = None
    reviews_data = []
    amount_temp = 0
    while (cursor and cursor != previous_cursor) and (amount_temp < int(amount)):
        start_time = time.time()
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
        amount_temp += 20
        end_time = time.time()
        callback((20/total)*100,end_time-start_time)
    reviews_df = pd.DataFrame(reviews_data)
    print(f'{file_path}/{language}.xlsx')
    reviews_df.to_excel(f'{file_path}/{language}.xlsx', sheet_name='data', index=False)