class Results:

    required_attributes = ["targets", "links_followed", "links_error"]

    def __init__(self, **kwargs):
        self.fields = kwargs.keys()
        for keys, values in kwargs.items():
            self.__setattr__(keys, values)
        for attribute in self.required_attributes:
            if attribute not in kwargs:
                self.__setattr__(attribute, [])
