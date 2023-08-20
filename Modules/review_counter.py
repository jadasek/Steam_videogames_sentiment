import requests
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf8')

if len(sys.argv) > 2:
    game_name = sys.argv[1]
    language = sys.argv[2]
else:
    raise ValueError("Missing required parameters: game_name and language")

def get_review_count(game_name: str, language: list) -> list:
    review_count = []
    language = language.split(',')
    print(language)
    for lang in language:
        url = f"https://store.steampowered.com/appreviews/{game_name}?json=1&language={lang}&purchase_type=all"
        response = requests.get(url)
        data = response.json()
        review_count.append(data["query_summary"]["total_reviews"])
    return review_count

review_count = get_review_count(game_name, language)
print(review_count)
