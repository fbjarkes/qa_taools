from datetime import datetime, timedelta
import logging as logger

import pandas as pd
import requests_cache
import pandas_datareader.data as web


class WebDataprovider:
    """
    """

    logger.basicConfig(level=logger.INFO, format='%(filename)s: %(message)s')

    def __add_ticker(self, ticker, df):
        df['Ticker'] = ticker
        return df

    def __init__(self, cache_name='cache', expire_days=3):
        expire_after = (None if expire_days is (None or 0) else timedelta(days=expire_days))
        self.session = requests_cache.CachedSession(cache_name=cache_name, backend='sqlite', expire_after=expire_after)

        logger.info("Using cache '{0}' with {1} items. Expires ?".format(cache_name, len(self.session.cache.responses)))

    def get_data_parallel(self, tickers, from_date, to_date, workers=2, timeframe='day', provider='google'):
        # TODO: concurrent data fetching
        # TODO: adding latest, i.e. current (delayed) price if market is open
        pass

    def get_data(self, ticker, from_date, to_date, timeframe='day', provider='google'):
        """
        Note this will only get historical data.
        :param ticker:
        :param from_date:
        :param to_date:
        :param timeframe:
        :param provider:
        :return:
        """
        logger.info("%s: %s to %s, provider=%s" % (ticker, from_date, to_date, provider))

        start = datetime.strptime(from_date, "%Y-%m-%d")
        end = datetime.strptime(to_date, "%Y-%m-%d")
        data = web.DataReader(ticker, provider, start=start, end=end, session=self.session, pause=1)

        # From: http://blog.yhat.com/posts/stock-data-python.html
        transdat = data.loc[:, ["Open", "High", "Low", "Close"]]
        if timeframe == 'week':
            transdat["week"] = pd.to_datetime(transdat.index).map(lambda x: x.isocalendar()[1])  # Identify weeks
            transdat["year"] = pd.to_datetime(transdat.index).map(lambda x: x.isocalendar()[0])

            grouped = transdat.groupby(list(set(["year", "week"])))  # Group by year and other appropriate variable
            dataframes = pd.DataFrame({"Open": [], "High": [], "Low": [], "Close": []})
            for name, group in grouped:
                df = pd.DataFrame({"Open": group.iloc[0, 0], "High": max(group.High), "Low": min(group.Low),
                                   "Close": group.iloc[-1, 3]}, index=[group.index[0]])
                dataframes = dataframes.append(df)

            sorted = dataframes.sort_index()
            return self.__add_ticker(ticker, sorted)
        else:
            return self.__add_ticker(ticker, transdat)
