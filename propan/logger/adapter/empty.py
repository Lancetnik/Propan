from ..model.usecase import LoggerUsecase


class EmptyLogger(LoggerUsecase):
    def info(self, message: str):
        pass

    def debug(self, message: str):
        pass

    def error(self, message: str):
        pass

    def success(self, message: str):
        pass

    def warning(self, message: str):
        pass

    def catch(self, func, reraise: bool = False):
        async def wrapped(*args, **kwargs):
            return await func(*args, **kwargs)
        return wrapped
