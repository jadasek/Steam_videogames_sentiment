# %%
import snscrape.modules.twitter as sntwitter
import pandas as pd
import re
from tqdm.auto import tqdm
from datetime import datetime, timedelta

games = ['CSGO', 'Valorant', 'Overwatch', 'Apex Legends', 'PUBG', 'Fortnite', 'League of Legends', 'Minecraft', 'Roblox', '(Grand Theft Auto OR GTA)', '(Borderlands2 OR Borderlands 2)', '(RDR2 OR Red Dead Redemption 2)', 'Detroit Become Human', 'Skyrim', 'Dark Souls', '(Portal OR Portal 2)', '(Breath of the wild OR BOTW)', 'Mario', 'Pokemon', 'Terraria', 'Animal Crossing', '(The witcher 3 OR The witcher OR TW3)', '(COD OR Call of Duty)', 'God of War']
types = ['Music', '(plot OR story)', 'Gameplay', '(graphics OR graphic)', '(characters OR character)', 'UI', 'Enviroment', '(Control OR controls)', 'community']
now = datetime.now()
date_only = now.date()

until = date_only
since = date_only - timedelta(7)

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

# Przeglądamy 500 tweetów dla danego hasztagu
pbar2 = tqdm(total=735)
pbar = tqdm(total=len(games))
s = ' -'.join(types)
for i in range(0,735,7):
    until_temp = until - timedelta(i)
    since_temp = since - timedelta(i)
    pbar.reset()
    for game in games:
        for t in types:
            try:
                scraper = sntwitter.TwitterSearchScraper(f'{game} {t} until:{until_temp} since:{since_temp}')
                for i, tweet in enumerate(scraper.get_items()):
                    try:
                        data = [
                            tweet.date,
                            tweet.id,
                            tweet.rawContent,
                            tweet.user.username,
                            tweet.likeCount,
                            tweet.retweetCount,
                            tweet.viewCount,
                            tweet.lang,
                            tweet.links,
                            tweet.media,
                            game,
                            t
                        ]
                        if data[4] == data[5]:
                            continue
                        else:
                            data[2] = pre_process(data[2])
                            if data[2] == ' ' or data[2] == '':
                                continue
                            else:
                                tweets.append(data)
                                if i >= 500:
                                    break
                    except:
                        continue
            except:
                break

        scraper = sntwitter.TwitterSearchScraper(f'{game} until:{until_temp} since:{since_temp} -{s}')
        try:
            for i, tweet in enumerate(scraper.get_items()):
                try:
                    data = [
                        tweet.date,
                        tweet.id,
                        tweet.rawContent,
                        tweet.user.username,
                        tweet.likeCount,
                        tweet.retweetCount,
                        tweet.viewCount,
                        tweet.lang,
                        tweet.links,
                        tweet.media,
                        game,
                        "other"
                    ]
                    if data[4] == data[5]:
                        continue
                    else:
                        data[2] = pre_process(data[2])
                        if data[2] == ' ' or data[2] == '':
                            continue
                        else:
                            tweets.append(data)
                            if i >= 500:
                                break
                except:
                    continue
        except:
            break
        pbar.update(1)
    pbar2.update(7)

a=pd.DataFrame(tweets, columns=['date', 'id', 'content', 'username','like_count','retweet_count', 'view_count', 'language', 'links','media','game','type'])

a.head()



# %%
a['id'] = a['id'].astype('string')
a['date'] = a['date'].dt.tz_localize(None)
a.to_excel(r'export_dataframe.xlsx', index=False)