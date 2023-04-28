import tweepy
import driver
import os


def sendTweet(text):
    """
    Sends a tweet with the given text
    :param text: The text of the tweet
    """
    while True:
        try:
            client = tweepy.Client(
                consumer_key=os.getenv("TWITTER_CONSUMER_KEY"),
                consumer_secret=os.getenv("TWITTER_CONSUMER_SECRET"),
                access_token=os.getenv("TWITTER_ACCESS_TOKEN"),
                access_token_secret=os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
            )
            client.create_tweet(text=text)
            break
        except tweepy.TooManyRequests as e:
            print("Running backup method...")
            driver.sendTweet(text)
            break
        except Exception:
            pass
