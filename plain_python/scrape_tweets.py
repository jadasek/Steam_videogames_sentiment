# %%
import snscrape.modules.twitter as sntwitter
import pandas as pd
import re
from tqdm.notebook import tqdm

game = 'CSGO'
scraper = sntwitter.TwitterSearchScraper(f'{game} min_replies:1 min_faves:10')

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
pbar = tqdm(total=500)
for i, tweet in enumerate(scraper.get_items()):
    data = [
        tweet.date,
        tweet.id,
        tweet.rawContent,
        tweet.user.username,
        tweet.likeCount,
        tweet.retweetCount,
        tweet.lang
    ]
    if data[4] == data[5]:
        continue
    else:
        data[2] = pre_process(data[2])
        if data[2] == ' ' or data[2] == '':
            continue
        else:
            tweets.append(data)
            pbar.update(1)
            if len(tweets) >= 500:  # Przerywamy pętlę po pobraniu 500 tweetów
                break

a=pd.DataFrame(tweets, columns=['date', 'id', 'content', 'username','like_count','retweet_count', 'language'])
a.head()



# %%
a['date'] = a['date'].dt.tz_localize(None)
a.to_excel(r'export_dataframe.xlsx', index=False)