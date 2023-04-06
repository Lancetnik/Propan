class Singlethon:
    _instanse = None

    def __new__(cls, *args, **kwargs):
        if cls._instanse is None:
            cls._instanse = super().__new__(cls)
        return cls._instanse
