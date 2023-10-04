import tweepy
import logging
from kafka import KafkaProducer

consumerKey="ySKhVkOKCtiliQwgK3H3pCUQz"
consumerSecret="5m36DAuIEYh7nJamCKZKFrzIFleBJlo6TIuTsoSzi2QRsZy09i"
accessToken="1181807188337143808-SbNugSw1zNuRRA4vlDlNffUBfd6Eg0"
accessTokenSecret="e7whEpJLnQNAeztQhgmnDp3cod8GcFQG4yhIMUbzMHBFC"

producer = KafkaProducer(bootstrap_servers='localhost:9092')
topic_name = "twitter"

class MyListener(tweepy.Stream):
    def on_data(self, raw_data):
        logging.info(raw_data)
        producer.send(topic_name, value=raw_data)
        return True

    def on_error(self, status_code):
        if status_code == 420:
            return False
 
twitter_stream = MyListener(consumerKey, consumerSecret, accessToken, accessTokenSecret)
twitter_stream.filter(track=['#FTX', 'Sam Bankman-Fried'], languages=["en"])
