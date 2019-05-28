from datetime import date
from pathlib import Path
from urllib.parse import urlencode

import requests

from .utils import parse_edgar_rss_feed


class Downloader:
    def __init__(self, download_folder=None):
        print("Welcome to the SEC EDGAR Downloader!")

        if download_folder is None:
            self._download_folder = Path.home().joinpath("Downloads")
        else:
            self._download_folder = Path(download_folder).expanduser().resolve()

        print(f"Company filings will be saved to: {self._download_folder}")

        self._sec_base_url = "https://www.sec.gov"
        self._sec_edgar_base_url = f"{self._sec_base_url}/cgi-bin/browse-edgar?"

    # TODO: allow users to specify before date
    def _form_url(self, ticker, filing_type):
        # Put into required format: YYYYMMDD
        before_date = date.today().strftime("%Y%m%d")
        query_params = {
            "action": "getcompany",
            "owner": "exclude",
            "start": 0,
            "count": 100,  # TODO: Allow users to pass this in
            "CIK": ticker,
            "type": filing_type,
            "dateb": before_date,
            "output": "atom",
        }
        return f"{self._sec_edgar_base_url}{urlencode(query_params)}"

    def _download_filings(
        self, edgar_search_url, filing_type, ticker, num_filings_to_download
    ):
        filing_document_info = parse_edgar_rss_feed(
            edgar_search_url, num_filings_to_download
        )

        # number of filings available may be less than the number requested
        num_filings_to_download = len(filing_document_info)

        if num_filings_to_download == 0:
            print(f"No {filing_type} documents available for {ticker}.")
            return 0

        print(
            f"{num_filings_to_download} {filing_type} documents available for {ticker}.",
            "Beginning download...",
        )

        for doc_info in filing_document_info:
            resp = requests.get(doc_info.url, stream=True)
            resp.raise_for_status()

            save_path = self._download_folder.joinpath(
                "sec_edgar_filings", ticker, filing_type, doc_info.filename
            )

            # Create all parent directories as needed. For example, if we have the
            # directory /hello and we want to create /hello/world/my/name/is/bob.txt,
            # this would create all the directories leading up to bob.txt.
            save_path.parent.mkdir(parents=True, exist_ok=True)

            with open(save_path, "wb") as f:
                for chunk in resp.iter_content(chunk_size=1024):
                    # filter out keep-alive chunks
                    if chunk:  # pragma: no branch
                        f.write(chunk)

        print(f"{filing_type} filings for {ticker} downloaded successfully.")

        return num_filings_to_download

    def _get_filing_wrapper(self, filing_type, ticker_or_cik, num_filings_to_download):
        num_filings_to_download = int(num_filings_to_download)
        if num_filings_to_download < 1:
            raise ValueError(
                "Please enter a number greater than 1 for the number of filings to download."
            )
        ticker_or_cik = str(ticker_or_cik).strip().upper().lstrip("0")
        print(f"\nGetting {filing_type} filings for {ticker_or_cik}.")
        filing_url = self._form_url(ticker_or_cik, filing_type)
        return self._download_filings(
            filing_url, filing_type, ticker_or_cik, num_filings_to_download
        )

    """
    Generic download methods
    """

    def get_8k_filings(self, ticker_or_cik, num_filings_to_download=100):
        filing_type = "8-K"
        return self._get_filing_wrapper(
            filing_type, ticker_or_cik, num_filings_to_download
        )

    def get_10k_filings(self, ticker_or_cik, num_filings_to_download=100):
        filing_type = "10-K"
        return self._get_filing_wrapper(
            filing_type, ticker_or_cik, num_filings_to_download
        )

    def get_10q_filings(self, ticker_or_cik, num_filings_to_download=100):
        filing_type = "10-Q"
        return self._get_filing_wrapper(
            filing_type, ticker_or_cik, num_filings_to_download
        )

    # Differences explained here: https://www.sec.gov/divisions/investment/13ffaq.htm
    def get_13f_nt_filings(self, ticker_or_cik, num_filings_to_download=100):
        filing_type = "13F-NT"
        return self._get_filing_wrapper(
            filing_type, ticker_or_cik, num_filings_to_download
        )

    def get_13f_hr_filings(self, ticker_or_cik, num_filings_to_download=100):
        filing_type = "13F-HR"
        return self._get_filing_wrapper(
            filing_type, ticker_or_cik, num_filings_to_download
        )

    def get_sc_13g_filings(self, ticker_or_cik, num_filings_to_download=100):
        filing_type = "SC 13G"
        return self._get_filing_wrapper(
            filing_type, ticker_or_cik, num_filings_to_download
        )

    def get_sd_filings(self, ticker_or_cik, num_filings_to_download=100):
        filing_type = "SD"
        return self._get_filing_wrapper(
            filing_type, ticker_or_cik, num_filings_to_download
        )

    """
    Bulk download methods
    """

    def get_all_available_filings(self, ticker_or_cik, num_filings_to_download=100):
        total_dl = 0
        total_dl += self.get_8k_filings(ticker_or_cik, num_filings_to_download)
        total_dl += self.get_10k_filings(ticker_or_cik, num_filings_to_download)
        total_dl += self.get_10q_filings(ticker_or_cik, num_filings_to_download)
        total_dl += self.get_13f_nt_filings(ticker_or_cik, num_filings_to_download)
        total_dl += self.get_13f_hr_filings(ticker_or_cik, num_filings_to_download)
        total_dl += self.get_sc_13g_filings(ticker_or_cik, num_filings_to_download)
        total_dl += self.get_sd_filings(ticker_or_cik, num_filings_to_download)
        return total_dl
