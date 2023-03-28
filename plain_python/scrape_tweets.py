# %%
import snscrape.modules.twitter as sntwitter
import pandas as pd

scraper = sntwitter.TwitterSearchScraper('CSGO min_replies:1 min_faves:10')

tweets = []

# Przeglądamy 50 najpopularniejszych tweetów dla danego hasztagu
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
    tweets.append(data)  # Dodajemy treść tweetu do listy tweets
    if i > 500:  # Przerywamy pętlę, gdy pobraliśmy 50 tweetów
        break

a=pd.DataFrame(tweets, columns=['date', 'id', 'content', 'username','like_count','retweet_count', 'language'])
a.head()


# %%
a['date'] = a['date'].dt.tz_localize(None)
a.to_excel(r'C:\Users\tymot\Desktop\export_dataframe.xlsx', index=False)