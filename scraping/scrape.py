from steam_review_scraper import search_game_id
from steam_review_scraper import get_game_review 
import pandas as pd

games = ['Detroit Become Human', 'Dark Souls 3', 'Portal 2', 'Terraria', 'The witcher 3']
game_ids = []
output = pd.DataFrame(columns=['user','playtime','user_url','post_date','helpfulness','review','recommend','early_access_review','game_id'])

for i in games:
    ids = search_game_id(i)
    game = ids.iloc[0]['id']
    game_ids.append(game)

for i in game_ids:
    print ("\033[A                             \033[A")
    print ("\033[A                             \033[A")
    print(f'{int(((game_ids.index(i))/len(game_ids))*100)}%')
    print(' ')
    reviews = get_game_review(i)
    reviews['game_id'] = i
    output = pd.concat([output,reviews])

output = output.drop(['user_url','user'], axis=1)
output.to_excel('C:/Users/tymot/Desktop/Nowy folder (3)/output.xlsx', engine='xlsxwriter')