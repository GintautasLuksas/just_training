import pandas as pd

df = pd.read_csv("C:/Users/user/PycharmProjects/just_training/data/train.csv")

df.info()
df.isnull().sum()
df.shape

df.head()