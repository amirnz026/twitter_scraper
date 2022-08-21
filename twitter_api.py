import requests
import configparser
import pandas as pd
from models import Tweet, is_positive_or_negative

# read configs
config = configparser.RawConfigParser()
config.read('config.ini')

api_key = config['twitter']['api_key']
api_key_secret = config['twitter']['api_key_secret']

access_token = config['twitter']['access_token']
access_token_secret = config['twitter']['access_token_secret']
bearer_token = config['twitter']['bearer_token']

search_url = "https://api.twitter.com/2/tweets/search/recent"

# Optional params: start_time,end_time,since_id,until_id,max_results,next_token,
# expansions,tweet.fields,media.fields,poll.fields,place.fields,user.fields
query_params = {'query': 'ワクチン', 'tweet.fields': "created_at"}


def bearer_oauth(r):
    """
    Method required by bearer token authentication.
    """

    r.headers["Authorization"] = f"Bearer {bearer_token}"
    r.headers["User-Agent"] = "v2RecentSearchPython"
    return r


def connect_to_endpoint(url, params):
    response = requests.get(url, auth=bearer_oauth, params=params)
    print(response.status_code)
    if response.status_code != 200:
        raise Exception(response.status_code, response.text)
    return response.json()


def main():
    while True:
        json_response = connect_to_endpoint(search_url, query_params)
        for item in json_response['data']:
            tweets_df = pd.read_csv('tweets.csv')
            tweets_df = tweets_df.drop_duplicates(subset=['Tweet_link'])
            tweet = Tweet(item['text'], item['id'], item['created_at'])
            pos_or_neg, words = is_positive_or_negative(tweet)  # 1 positive -1 negative 0 neutral
            if pos_or_neg == 1:
                new_tweet_df = pd.DataFrame({
                    'Date': tweet.created_at_date,
                    'Time': tweet.created_at_time,
                    'Positive': 1,
                    'Negative': ' ',
                    'Tweet': tweet.tweet_main_text,
                    'Translated_Tweet': tweet.translated_tweet_text,
                    'Keyword(s)': words,
                    'Tweet_link': f"https://twitter.com/twitter/status/{tweet.tweet_id}"
                })
                tweets_df = tweets_df.append(new_tweet_df, ignore_index=True)
                tweets_df.to_csv('tweets.csv', index=False)
                continue

            elif pos_or_neg == -1:
                new_tweet_df = pd.DataFrame({
                    'Date': tweet.created_at_date,
                    'Time': tweet.created_at_time,
                    'Positive': ' ',
                    'Negative': 1,
                    'Tweet': tweet.tweet_main_text,
                    'Translated_Tweet': tweet.translated_tweet_text,
                    'Keyword(s)': words,
                    'Tweet_link': f"https://twitter.com/twitter/status/{tweet.tweet_id}"

                })
                tweets_df = tweets_df.append(new_tweet_df, ignore_index=True)
                tweets_df.to_csv('tweets.csv', index=False)
                continue


if __name__ == "__main__":
    main()
