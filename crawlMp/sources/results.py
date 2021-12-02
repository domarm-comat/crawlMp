from crawlMp import share_manager


class Results:

    def __init__(self, shared=False):
        # Required fields
        self.targets_found = share_manager.list() if shared else []
        self.links_followed = share_manager.list() if shared else []
        self.links_failed = share_manager.list() if shared else []

    def reset(self):
        self.targets_found[:] = []
        self.links_followed[:] = []
        self.links_failed[:] = []
