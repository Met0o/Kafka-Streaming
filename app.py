import os
#os.environ['PYSPARK_SUBMIT_ARGS'] = '--packages org.apache.spark:spark-streaming-kafka-0-10_2.13:3.2.1,org.apache.kafka:kafka-clients:3.2.1 pyspark-shell'
os.environ["JAVA_HOME"] = "/usr/lib/jvm/java-11-openjdk-amd64"
os.environ["SPARK_HOME"] = "/home/msimeonov/sources/spark-3.1.2-bin-hadoop3.2/"

#chmod +x /home/msimeonov/sources/spark-3.1.2-bin-hadoop3.2/bin/*

#import findspark
#findspark.init('/home/msimeonov/sources/spark-3.1.2-bin-hadoop3.2')

from pyspark.conf import SparkConf
from pyspark.context import SparkContext
from pyspark.sql import functions as F
from pyspark.sql.functions import explode
from pyspark.sql.functions import split
from pyspark.sql.types import StringType, StructType, StructField, FloatType
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, udf
from pyspark.ml.feature import RegexTokenizer
import re
from textblob import TextBlob

# remove_links
def cleanTweet(tweet: str) -> str:
    tweet = re.sub(r'http\S+', '', str(tweet))
    tweet = re.sub(r'bit.ly/\S+', '', str(tweet))
    tweet = tweet.strip('[link]')

    # remove users
    tweet = re.sub('(RT\s@[A-Za-z]+[A-Za-z0-9-_]+)', '', str(tweet))
    tweet = re.sub('(@[A-Za-z]+[A-Za-z0-9-_]+)', '', str(tweet))

    # remove puntuation
    my_punctuation = '!"$%&\'()*+,-./:;<=>?[\\]^_`{|}~•@â'
    tweet = re.sub('[' + my_punctuation + ']+', ' ', str(tweet))

    # remove number
    tweet = re.sub('([0-9]+)', '', str(tweet))

    # remove hashtag
    tweet = re.sub('(#[A-Za-z]+[A-Za-z0-9-_]+)', '', str(tweet))
    
    # remove white spaces
    tweet = re.sub(' +', ' ', str(tweet))
    
    # strip any leading and trailing spaces.
    tweet = tweet.strip()

    return tweet


# Create a function to get the subjectifvity
def getSubjectivity(tweet: str) -> float:
    return TextBlob(tweet).sentiment.subjectivity


# Create a function to get the polarity
def getPolarity(tweet: str) -> float:
    return TextBlob(tweet).sentiment.polarity


def getSentiment(polarityValue: int) -> str:
    if polarityValue < 0:
        return 'Negative'
    elif polarityValue == 0:
        return 'Neutral'
    else:
        return 'Positive'


# epoch
def write_row_in_mongo(df, epoch_id):
    mongoURL = "mongodb+srv://mongoadmin:mongoadmin@cluster0.k6w8uci.mongodb.net/TwitterDB.Tweets" \
               "?retryWrites=true&w=majority"
    df.write.format("mongo").mode("append").option("uri", mongoURL).save()
    pass

if __name__ == "__main__":
    spark = SparkSession \
        .builder \
        .appName("Tweets") \
        .config("spark.mongodb.input.uri",
                "mongodb+srv://mongoadmin:mongoadmin@cluster0.k6w8uci.mongodb.net/TwitterDB.Tweets/?retryWrites=true&w=majority") \
        .config("spark.jars.packages", "org.mongodb.spark:mongo-spark-connector_2.12:3.0.2,org.apache.spark:spark-sql-kafka-0-10_2.12:3.1.2") \
        .getOrCreate()

    df = spark \
        .readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "localhost:9092") \
        .option("subscribe", "twitter") \
        .load()

    mySchema = StructType([StructField("text", StringType(), True)])
    # Get only the "text" from the information we receive from Kafka. The text is the tweet produced by a user
    values = df.select(from_json(df.value.cast("string"), mySchema).alias("tweet"))

    df1 = values.select("tweet.*")
    clean_tweets = F.udf(cleanTweet, StringType())
    raw_tweets = df1.withColumn('processed_text', clean_tweets(col("text")))
    # udf_stripDQ = udf(stripDQ, StringType())

    subjectivity = F.udf(getSubjectivity, FloatType())
    polarity = F.udf(getPolarity, FloatType())
    sentiment = F.udf(getSentiment, StringType())

    subjectivity_tweets = raw_tweets.withColumn('subjectivity', subjectivity(col("processed_text")))
    polarity_tweets = subjectivity_tweets.withColumn("polarity", polarity(col("processed_text")))
    sentiment_tweets = polarity_tweets.withColumn("sentiment", sentiment(col("polarity")))

    '''
    all about tokenization
    '''
    # Create a tokenizer that Filter away tokens with length < 3, and get rid of symbols like $,#,...
    tokenizer = RegexTokenizer().setPattern("[\\W_]+").setMinTokenLength(3).setInputCol("processed_text").setOutputCol(
        "tokens")

    # Tokenize tweets
    tokenized_tweets = tokenizer.transform(raw_tweets)

    # en sortie on a
    tweets_df = df1.withColumn('word', explode(split(col("text"), ' '))).groupby('word').count().sort('count',
                                                                                                      ascending=False).filter(
        col('word').contains('#'))

    query = sentiment_tweets.writeStream.queryName("test_tweets") \
        .foreachBatch(write_row_in_mongo).start().awaitTermination()