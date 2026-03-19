import pandas as pd


# 1.Count Requests: Calculate the total number of lines processed (excluding the header).
# 2. IP Breakdown: Create a dictionary where each key is an ip_address and the value is the count of how many times that IP appeared.
# 3. Error Tracker: Identify which IPs triggered a 500 status code.
# 4. Performance: Calculate the average response_time for all successful requests (status_code 200).

df = pd.read_csv(r'C:\Users\user\PycharmProjects\just_training\data\pandas.csv')

print(df.info())

