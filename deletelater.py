import pandas as pd

# df = pd.read_csv('MOCK_DATA (1).csv')
# df = df.sort_values('Date')
# print(df)
# df.to_csv('MOCK_DATA (1).csv', index=False)
even_hours = [0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22]

tweets_df = pd.read_csv('MOCK_DATA (1).csv')
print(tweets_df.to_string())
dates = tweets_df['Date'].unique()
print(dates)
results_csv = pd.DataFrame(columns=['Date', 'Time', 'Positive', 'Negative', 'Total'])
for date in dates:
    for hour in even_hours:
        prev_hour = even_hours[even_hours.index(hour) - 1] + 1
        prev_prev_hour = even_hours[even_hours.index(hour) - 1]

        number_of_positives = tweets_df[(tweets_df['Date'] == date) &
                                        (tweets_df['Hour'] == prev_hour) &
                                        (tweets_df['Positive'] == 1)].shape[0]

        number_of_negatives = tweets_df[(tweets_df['Date'] == date) &
                                        (tweets_df['Hour'] == prev_hour) &
                                        (tweets_df['Negative'] == 1)].shape[0]

        number_of_positives += tweets_df[(tweets_df['Date'] == date) &
                                         (tweets_df['Hour'] == prev_prev_hour) &
                                         (tweets_df['Positive'] == 1)].shape[0]

        number_of_negatives += tweets_df[(tweets_df['Date'] == date) &
                                         (tweets_df['Hour'] == prev_prev_hour) &
                                         (tweets_df['Negative'] == 1)].shape[0]

        new_row = pd.DataFrame([{
            'Date': date,
            'Time': f'{hour}:00',
            'Positive': number_of_positives,
            'Negative': number_of_negatives,
            'Total': number_of_positives + number_of_negatives
        }], )
        results_csv = results_csv.append(new_row, ignore_index=True)
        print(results_csv)
        if number_of_positives and number_of_negatives:
            break
print(results_csv)
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
results_csv.to_csv('Mock_Results.csv', index=False)
print(results_csv)
print('kirrr')
