import copy


class Results:

    def __init__(self, copy_values=False, **kwargs):
        # Required fields
        self.targets_found = []
        self.links_followed = []
        self.links_failed = []
        # Required fields
        self.fields = kwargs.keys()
        for keys, values in kwargs.items():
            self.__setattr__(keys, values if not copy_values else copy.deepcopy(values))
