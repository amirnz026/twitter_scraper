from googletrans import Translator
import pandas as pd

translator = Translator()

even_hours = [0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22]


class Tweet:
    def __init__(self, tweet_main_text, tweet_id, created_at):
        self.created_at_date = ''
        self.created_at_hour = ''
        self.created_at_minute = ''
        self.set_zulu_to_utc(created_at)

        self.tweet_main_text = tweet_main_text
        self.translated_tweet_text = translator.translate(tweet_main_text, dest='en').text
        self.tweet_id = tweet_id
        self.tweet_link = f"https://twitter.com/twitter/status/{self.tweet_id}"

    def __str__(self):
        return f"{self.tweet_main_text}\n{self.translated_tweet_text}" \
               f"\n{self.tweet_id}\n{self.created_at_date}" \
               f"\n{self.created_at_time}\n\n\n\n"

    def set_zulu_to_utc(self, zulu_time):
        date_time = str(zulu_time).split('T')
        self.created_at_date = '.'.join(date_time[0].split('-')[:3])
        self.created_at_hour = date_time[1].split(':')[0]
        self.created_at_minute = date_time[1].split(':')[1]


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


def tweet_csv_creator(json_file):
    for item in json_file['data']:
        tweets_df = pd.read_csv('tweets.csv')
        tweets_df = tweets_df.drop_duplicates(subset=['Tweet_link'])
        tweet = Tweet(item['text'], item['id'], item['created_at'])
        pos_or_neg, words = is_positive_or_negative(tweet)  # 1 positive -1 negative 0 neutral
        if pos_or_neg == 1:
            new_tweet_df = pd.DataFrame({
                'Date': tweet.created_at_date,
                'Hour': tweet.created_at_hour,
                'Minute': tweet.created_at_minute,
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
                'Hour': tweet.created_at_hour,
                'Minute': tweet.created_at_minute,
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


def results_csv_creator():
    tweets_df = pd.read_csv('tweets.csv')
    dates = tweets_df['Date'].unique()
    results_csv = pd.DataFrame(columns=['Date', 'Time', 'Positive', 'Negative', 'Total'])
    for date in dates:
        for hour in even_hours:
            prev_hour = even_hours[even_hours.index(hour) - 1] + 1
            prev_prev_hour = even_hours[even_hours.index(hour) - 1]

            number_of_positives = tweets_df[(tweets_df['Date'] == date) &
                                            (tweets_df['Hour'] == prev_hour) &
                                            (tweets_df['Positive'] == '1')].shape[0]

            number_of_negatives = tweets_df[(tweets_df['Date'] == date) &
                                            (tweets_df['Hour'] == prev_hour) &
                                            (tweets_df['Negative'] == '1')].shape[0]

            number_of_positives += tweets_df[(tweets_df['Date'] == date) &
                                             (tweets_df['Hour'] == prev_prev_hour) &
                                             (tweets_df['Positive'] == '1')].shape[0]

            number_of_negatives += tweets_df[(tweets_df['Date'] == date) &
                                             (tweets_df['Hour'] == prev_prev_hour) &
                                             (tweets_df['Negative'] == '1')].shape[0]
            print(date)
            print(hour)
            print(number_of_positives)
            print(number_of_negatives)

            new_row = pd.DataFrame([{
                'Date': date,
                'Time': f'{hour}:00',
                'Positive': number_of_positives,
                'Negative': number_of_negatives,
                'Total': number_of_positives + number_of_negatives
            }], )
            results_csv = results_csv.append(new_row, ignore_index=True)
            # if number_of_positives and number_of_negatives:
            #     break
    results_csv = results_csv.drop_duplicates(subset=['Date', 'Time'])
    results_csv = results_csv[results_csv['Total'] != 0]
    dates = results_csv['Date'].unique()
    for date in dates:
        sum_row = pd.DataFrame([{
            'Date': date,
            'Time': 'summary',
            'Positive': results_csv[results_csv['Date'] == date]['Positive'].values.sum(),
            'Negative': results_csv[results_csv['Date'] == date]['Negative'].values.sum(),
            'Total': results_csv[results_csv['Date'] == date]['Total'].values.sum(),
        }])
        new_row_index = results_csv[results_csv['Date'] == date].index[-1]
        results_csv = pd.concat(
            [results_csv.iloc[:new_row_index + 1], sum_row, results_csv.iloc[(new_row_index + 1):]]).reset_index(
            drop=True)
    results_csv.to_csv('results.csv', index=False)
