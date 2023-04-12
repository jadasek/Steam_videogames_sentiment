# %%
import snscrape.modules.twitter as sntwitter
import pandas as pd
import re
from tqdm.auto import tqdm
from datetime import datetime, timedelta

games = ['CSGO', 'Valorant', 'Overwatch', 'Apex Legends', 'PUBG', 'Fortnite', 'LOL', 'Minecraft', 'Roblox', 'GTAV']
now = datetime.now()
date_only = now.date()

until = date_only
since = date_only - timedelta(1)

tweets = []
def pre_process(text):
    # Usuwanie linków
    text = re.sub('http://\S+|https://\S+', '', text)
    text = re.sub('http[s]?://\S+', '', text)
    text = re.sub(r"http\S+", "", text)

    # Napraw wbudowane linki
    text = re.sub('&amp', 'and', text)
    text = re.sub('&lt', '<', text)
    text = re.sub('&gt', '>', text)

    # Usuwanie znaków nowej linii
    text = re.sub('[\r\n]+', ' ', text)
    
    # Usuwanie @
    text = re.sub(r'@\w+', '', text)
    
    # Usuwanie #
    text = re.sub(r'#\w+', '', text)

    # Usuń wielokrotności spacji
    text = re.sub('\s+',' ', text)
    
    # Przełóż na lowercase
    text = text.lower()
    return text

# Przeglądamy 500 najpopularniejszych tweetów dla danego hasztagu
pbar2 = tqdm(total=365)
pbar = tqdm(total=len(games))
for i in range(2,365,2):
    until_temp = until - timedelta(i)
    since_temp = since - timedelta(i)
    pbar.reset()
    for game in games:
        scraper = sntwitter.TwitterSearchScraper(f'{game} min_replies:1 min_faves:10 until:{until_temp} since:{since_temp}')
        for i, tweet in enumerate(scraper.get_items()):
            data = [
                tweet.date,
                tweet.id,
                tweet.rawContent,
                tweet.user.username,
                tweet.likeCount,
                tweet.retweetCount,
                tweet.lang,
                game
            ]
            if data[4] == data[5]:
                continue
            else:
                data[2] = pre_process(data[2])
                if data[2] == ' ' or data[2] == '':
                    continue
                else:
                    tweets.append(data)
                    if i >= 20:
                        break
        pbar.update(1)
    pbar2.update(2)

a=pd.DataFrame(tweets, columns=['date', 'id', 'content', 'username','like_count','retweet_count', 'language', 'game'])

a.head()



# %%
a['id'] = a['id'].astype('string')
a['date'] = a['date'].dt.tz_localize(None)
a.to_excel(r'export_dataframe.xlsx', index=False)