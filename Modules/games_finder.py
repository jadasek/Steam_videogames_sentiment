import requests
import sys
from difflib import get_close_matches

if len(sys.argv) > 1:
    game_name = sys.argv[1]
else:
    game_name = ""

def search_steam(game_name):
    url = "http://api.steampowered.com/ISteamApps/GetAppList/v0002/?format=json"
    result = []
    response = requests.get(url)
    data = response.json()
    apps = data["applist"]["apps"]
    app_names = [app["name"] for app in apps]
    closest_matches = get_close_matches(game_name, app_names, n=10, cutoff=0.6)
    for match in closest_matches:
        for app in apps:
            if app["name"] == match:
                result.append(f'Nazwa gry: {app["name"]}, ID gry: {app["appid"]}, Link do strony gry na Steam: https://store.steampowered.com/app/{app["appid"]}')
                break
    return result

results = search_steam(game_name)
for result in results:
    print(result)

