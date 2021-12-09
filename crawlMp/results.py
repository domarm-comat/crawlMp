from pandas import DataFrame

from crawlMp import share_manager


class Results:
    """
    Object to aggregate all results and errors.
    """

    def __init__(self, shared=False) -> None:
        """
        Create lists of results.
        If shared is True, all results are created from Shared manager.
        :param bool shared: shared or local list
        """
        # Required fields
        self.shared = shared
        self.hits = share_manager.list() if shared else []
        self.links_followed = share_manager.list() if shared else []
        self.links_skipped = share_manager.list() if shared else []
        self.hits_header = share_manager.list() if shared else ()
        self.links_header = share_manager.list() if shared else ()

    def reset(self) -> None:
        """
        Reset all results to empty list.
        :return: None
        """
        self.hits[:] = []
        self.links_followed[:] = []
        self.links_skipped[:] = []

    def dataframe(self) -> DataFrame:
        """
        Get pandas data frame of collected results.
        :return DataFrame: pandas DataFrame
        """
        return DataFrame(list(self.hits), columns=self.hits_header)
