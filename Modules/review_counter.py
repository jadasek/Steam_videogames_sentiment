import requests
from bs4 import BeautifulSoup

def get_review_count(game_name: str, language: str) -> int:
    url = f"https://store.steampowered.com/appreviews/{game_name}?json=1&language={language}"
    response = requests.get(url)
    data = response.json()
    review_count = data["query_summary"]["total_reviews"]
    return review_count

# Example usage
game_name = "1981160"
language = "en"
review_count = get_review_count(game_name, language)
print(review_count)
