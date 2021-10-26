"""Quant Test, October 2021

Author: Johan Öhlin <j.ohlin@lancaster.ac.uk>
Date (started):  Monday,  25 October 2021
Date (finished): Tuesday, 26 October 2021
"""

import numpy as np
import yfinance as yf
from dataclasses import dataclass

@dataclass
class Portfolio:
    """Portfolio class

    This dataclass is initialised with a portfolio of assets and the
    risk-free rate -- it will then calculate the Sortino ratio for the
    given assets. Bonus: Calculate portfolio beta compared to S&P 500.
    """
    asset_list: list
    risk_free_rate: float

    def __post_init__(self):
        self._download_data()
        self._portfolio_return()
        self._negative_excess_returns()

    def _download_data(self):
        """Download asset data from Yahoo Finance"""

        # initialising list to hold portfolio value data
        self.portf_value = 0
        self.portf_data = []

        # download ticker data for each asset in the portfolio
        for i in self.asset_list:

            # download price data for a single asset each iteration
            _ticker = yf.Ticker(i)
            _asset_data = _ticker.history(
                start="2020-10-25", end="2021-10-25", interval="1d"
            )

            # historical price data of a single asset added to list, one
            # at a time, avg price calculated to find portfolio value
            self.portf_value += _asset_data['Close'] / len(self.asset_list)

            # bonus: save asset data for calculation of portfolio beta
            self.portf_data.append(_asset_data['Close'])

    def _portfolio_return(self):
        """Find out the per cent return for the portfolio

        Here the first day of data is at index 0, while the last day of
        data is at index -1, as per Python's definition.
        """
        self.portf_return = (self.portf_value[-1]/self.portf_value[0] - 1) * 100

    def _negative_excess_returns(self):
        """Find Negative Excess Returns (NER) for the portfolio

        This function finds all instances of the portfolio's return
        being below its initial value plus the risk-free rate. These
        values are appended to a list `ner` where the values are then
        multiplied by a hundred, then squared.
        """
        self.ner = []
        for i in self.portf_value:
            if i < self.portf_value[0] + self.risk_free_rate:
                self.ner.append(
                    ((i / (self.portf_value[0]+self.risk_free_rate) - 1) * 100) ** 2)

    def portfolio_beta(self):
        """Calculate portfolio beta compared to S&P 500 Index

        This function downloads data for SPY, which is an ETF that
        tracks the S&P 500, calculates the portfolio beta, and returns
        the answer.
        """
        # download and use SPY as the market benchmark
        _bench_data = yf.download("SPY", "2020-10-25", "2021-10-25", progress=False)

        # calculate benchmark return, index 0 being last price and
        # index -1 being first price
        _bench_return = (_bench_data['Close'][0]/_bench_data['Close'][-1] - 1) * 100

        # initialise beta variable
        self.portf_beta = 0

        # looping through every asset in portfolio to create asset betas,
        # which are then combined to portfolio beta
        for i in self.portf_data:
            _asset_return = (i[0] / i[-1] - 1) * 100
            _asset_share = i[0] / self.portf_value[0]
            _asset_beta = (
                (_asset_return - self.risk_free_rate)
                / (_bench_return - self.risk_free_rate)
            )

            self.portf_beta += _asset_beta * _asset_share / len(self.portf_data)

        return self.portf_beta

    def sortino_ratio(self):
        """Calculate the Sortino ratio for the portfolio"""

        # calculate downside deviation by summing up values and taking
        # square root
        self.dwn_dev = np.sqrt(np.sum(self.ner))

        # calculate Sortino ratio according to formula
        sortino_ratio = (self.portf_return-self.risk_free_rate) / self.dwn_dev

        return sortino_ratio


def main():
    # unweighted portfolios
    port1_tickers = ["GLEN.L", "MRW.L", "AZN"]
    port2_tickers = ["LGEN.L", "TSCO", "GSK"]

    # SONIA as of 15 October 2021 is used as the risk-free rate, data
    # supplied from BoE
    risk_free_rate = 0.0502

    # initialise portfolios with given arguments
    portfolio1 = Portfolio(port1_tickers, risk_free_rate)
    portfolio2 = Portfolio(port2_tickers, risk_free_rate)

    # print results
    print("\033[4m" + "\t\tAsset allocation\t\t1 Yr Return %\tSortino ratio\tPortfolio beta" + "\033[0m")
    print(f"Portfolio 1\t{port1_tickers}\t{portfolio1.portf_return:.2f}\t\t{portfolio1.sortino_ratio():.3f}\t\t{portfolio1.portfolio_beta():.3f}")
    print(f"Portfolio 2\t{port2_tickers}\t{portfolio2.portf_return:.2f}\t\t{portfolio2.sortino_ratio():.3f}\t\t{portfolio2.portfolio_beta():.3f}")
    print("\nCredit: Johan Öhlin <j.ohlin@lancaster.ac.uk>")


if __name__ == "__main__":
    main()