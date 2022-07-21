from loguru import logger


empty = object()

IS_CONFIGURED = False

class UserSettingsHolder:
    def __init__(self, default_settings):
        self.__dict__['_deleted'] = set()
        self.default_settings = default_settings

    def __getattr__(self, name):
        if not name.isupper() or name in self._deleted:
            raise AttributeError
        try:
            return getattr(self.default_settings, name)
        except AttributeError as e:
            logger.warning(e)
            return None

    def __setattr__(self, name, value):
        self._deleted.discard(name)
        super().__setattr__(name, value)

    def __delattr__(self, name):
        self._deleted.add(name)
        if hasattr(self, name):
            super().__delattr__(name)


class LazySettings:
    _wrapped = None
    IS_CONFIGURED = IS_CONFIGURED

    def __init__(self):
        self._wrapped = empty

    def __getattr__(self, name):
        if name == "IS_CONFIGURED":
            return self.IS_CONFIGURED

        if self._wrapped is empty:
            self._setup(name)
        val = getattr(self._wrapped, name)
        self.__dict__[name] = val
        return val

    def __setattr__(self, name, value):
        if name == '_wrapped':
            self.__dict__.clear()
        else:
            self.__dict__.pop(name, None)
        super().__setattr__(name, value)

    def __delattr__(self, name):
        super().__delattr__(name)
        self.__dict__.pop(name, None)

    def configure(self, default_settings, **options):
        if self.IS_CONFIGURED is True:
            return self._wrapped

        holder = UserSettingsHolder(default_settings)
        for name, value in options.items():
            if not name.isupper():
                raise TypeError('Setting %r must be uppercase.' % name)
            setattr(holder, name, value)

        self._wrapped = holder
        if default_settings is not None:
            self.IS_CONFIGURED = True

settings = LazySettings()
