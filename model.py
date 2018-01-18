class Tweet():
    def __init__(self, tweetAsDictionary):
        self.url = tweetAsDictionary['url']
        self.timestamp = tweetAsDictionary['timestamp']
        self.userhandle = tweetAsDictionary['userhandle']
        self.tweetid = tweetAsDictionary['tweetid']
        self.text = tweetAsDictionary['text']


class Trade():
    def __init__(self, tradeAsDictionary):
        self.tickersymbol = tradeAsDictionary['tickersymbol']
        self.operation = tradeAsDictionary['operation']
        self.expirationdate = tradeAsDictionary['expirationdate']
        self.strikeprice = tradeAsDictionary['strikeprice']
        self.premium = tradeAsDictionary['premium']
