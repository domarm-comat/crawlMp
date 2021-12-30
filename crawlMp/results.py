from time import time
from typing import Tuple, List, Any

from pandas import DataFrame

from crawlMp import share_manager
from crawlMp.enums import Header_ref


class Results:
    """
    Object to aggregate all results and errors.
    """
    start_time: float = time()
    done_time: float = 0

    def __init__(self, hits_header: Tuple[Header_ref, ...], links_header: Tuple[Header_ref, ...],
                 shared: bool = False) -> None:
        """
        Create lists of results.
        If shared is True, all results are created from Shared manager.
        Header is defined as a list of tuples (Attribute name, Attribute type, Attribute unit).
        If Attribute has no unit use None.
        For example:
            ((Name, str, None), (Size, int, "byte"))
        :param tuple hits_header: header tuple
        :param tuple links_header: header tuple
        :param bool shared: shared or local list
        """
        # Required fields
        self.shared = shared
        self.hits: List[Any] = share_manager.list() if shared else []
        self.links_followed: List[Any] = share_manager.list() if shared else []
        self.links_skipped: List[Any] = share_manager.list() if shared else []
        self.hits_header = hits_header
        self.links_header = links_header

    @property
    def duration(self) -> float:
        return self.done_time - self.start_time

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
