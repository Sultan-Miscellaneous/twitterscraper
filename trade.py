import re


class Trade():

    def __init__(self, tweet):
        self.tweet = tweet

        self.contract_expiration_date = None
        self.contract_strike_price = None
        self.contract_premium = None
        self.ticker_symbol = None
        self.call_or_put = None
        self.operation = None
        try:
            self._parseUsingSingleRegex(tweet.text)
            self.isValidTrade = True
        except:
            print "failed to parse using single regex"
            pass

        try:
            self._parseTweet(self.tweet.text)
            self.isValidTrade = True
        except:
            print "failed to parse entirely"
            self.isValidTrade = False

    def isValid(self):
        return self.isValidTrade

    def saveToDb(self):
        # check if all variables are set then save to DB
        pass

    def _parseUsingSingleRegex(self, text):
        groupDictionary = re.match('^\$(?P<tickersymbol>\w+) (?P<operation>[A-z \/\. 0-9]*?)(?P<expirationdate>[0-9]+[\/\.][0-9]+) \$?(?P<strikeprice>[0-9\.]+)(?P<type>[PCpc]?) [Aa]?[Tt]? (?P<premium>[0-9]*\,?\.?[0-9]+\.?)', text).groupdict()
        self.contract_premium = groupDictionary['premium']
        self.contract_strike_price = groupDictionary['strikeprice']
        self.contract_expiration_date = groupDictionary['expirationdate']
        self.ticker_symbol = groupDictionary['tickersymbol']
        self.call_or_put = groupDictionary['type']
        
        #placeholder until we define a way to interpret the operation (new position, added, sold)
        self.operation = groupDictionary['operation']
        return groupDictionary

    def _parseRegex(self, text, regex):
        return re.match(regex, text).group(1)

    def _parseTweet(self, tweet_text):
        """
        Parses tweet and fills in instance variables

        Arguments:
        tweet_text: tweet as a string

        Return: None

        Throws exception if couldnt parse anything
        """
        processing_text = tweet_text
        if '@' in processing_text:
            return False

        # remove url from tweet
        processing_text = re.sub(
            'http[?s][^ ]+', '', processing_text, flags=re.IGNORECASE)

        # contract expiration date
        contract_expiration_date_result = self._parseRegex(
            processing_text, '.* ([0-9]+/[0-9]+).*')
        processing_text = processing_text.replace(
            contract_expiration_date_result, "")
        self.contract_expiration_date = contract_expiration_date_result

        # contract strike price
        contract_strike_price_result = self._parseRegex(
            processing_text, '.* ((\$)?([0-9]+(.[0-9]+)?[CP])).*')
        processing_text = processing_text.replace(
            contract_strike_price_result, "")
        # get the C or P at the end
        self.call_or_put = contract_strike_price_result[-1].upper()
        self.contract_strike_price = contract_strike_price_result[:-1]

        # contract premium
        contract_premium_result = self._parseRegex(
            processing_text, '.* (([0-9]+)?\.([0-9]+)).*')
        self.contract_premium = float(contract_premium_result)

        ticker_symbol_result = self._parseRegex(
            processing_text, '((\$)?([A-Z]+)) .*')
        # remove dollar sign
        self.ticker_symbol = ticker_symbol_result if ticker_symbol_result[
            0] == '$' else ticker_symbol_result[1:]
