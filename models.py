from googletrans import Translator
import pandas as pd

translator = Translator()


class Tweet:
    def __init__(self, tweet_main_text, tweet_id, created_at):
        self.created_at_date = ''
        self.created_at_time = ''
        self.set_zulu_to_utc(created_at)

        self.tweet_main_text = tweet_main_text
        self.translated_tweet_text = translator.translate(tweet_main_text, dest='en').text
        self.tweet_id = tweet_id

    def __str__(self):
        return f"{self.tweet_main_text}\n{self.translated_tweet_text}" \
               f"\n{self.tweet_id}\n{self.created_at_date}" \
               f"\n{self.created_at_time}\n\n\n\n"

    def set_zulu_to_utc(self, zulu_time):
        date_time = str(zulu_time).split('T')
        self.created_at_date = '.'.join(date_time[0].split('-')[:3])
        self.created_at_time = ':'.join(date_time[1].split(':')[:2])


def is_positive_or_negative(tweet: Tweet):
    positive_words = pd.read_csv('positive_words.csv')
    negative_words = pd.read_csv('negative_words.csv')

    is_positive = False
    is_negative = False

    positive_found_words = []
    negative_found_words = []

    tweet_split = tweet.translated_tweet_text.split(' ')
    for word in tweet_split:
        if is_positive is True and is_negative is True:
            return 0, positive_found_words + negative_found_words  # neutral
        if word in positive_words['positive'].unique():
            positive_found_words.append(word)
            is_positive = True
        if word in negative_words['negative'].unique():
            negative_found_words.append(word)
            is_negative = True

    if is_positive:
        return 1, positive_found_words  # positive
    elif is_negative:
        return -1, negative_found_words  # negative
    else:
        return False, False
