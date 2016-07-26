# Copyright (c) 2013-2016 Molly White
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os
import re
import tweepy
import urllib.request
from urllib.error import URLError
from offensive import tact
from html import unescape
from secrets import *
from bs4 import BeautifulSoup

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

auth = tweepy.OAuthHandler(C_KEY, C_SECRET)
auth.set_access_token(A_TOKEN, A_TOKEN_SECRET)
api = tweepy.API(auth)
tweets = api.user_timeline('VPKanye')


def get():
    try:
        response = urllib.request.urlopen("http://news.google.com/news?pz=1&cf=all&ned=us&hl=en&q=kaine&output=rss")
    except URLError as e:
        print(e.reason)
    else:
        html = BeautifulSoup(response.read(), "html.parser")
        items = html.find_all('item')
        for item in items:
            headline = item.title.string
            h_split = headline.split()

            # We don't want to use incomplete headlines
            if "..." in headline:
                continue

            # Try to weed out all-caps headlines
            if count_caps(h_split) >= len(h_split) - 3:
                continue

            # Skip anything too offensive
            if not tact(headline):
                continue

            # Remove attribution string
            if "-" in headline:
                headline = headline.split("-")[:-1]
                headline = ' '.join(headline).strip()

            if process(headline):
                break
            else:
                continue


def process(headline):
    headline = unescape(headline).strip()
    headline = re.sub(r'tim.{0,30}?\bkaine', "Kanye West", headline, flags=re.IGNORECASE)
    headline = re.sub(r'\bkaine\b', "Kanye", headline, flags=re.IGNORECASE)

    # # Don't tweet anything that's too long
    if len(headline) > 140:
        return False

    # # Don't tweet anything where a replacement hasn't been made
    if "Kanye" not in headline:
        return False
    else:
        return tweet(headline)


def tweet(headline):
    # # Check that we haven't tweeted this before
    for tweet in tweets:
        if headline == tweet.text:
            return False

    # Post tweet
    api.update_status(headline)
    return True


def count_caps(headline):
    count = 0
    for word in headline:
        if word[0].isupper():
            count += 1
    return count

if __name__ == "__main__":
    get()
