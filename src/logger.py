import logging


class Logger:

    def __init__(self, verbose: bool):
        logger = logging.getLogger(self.__class__.__name__)
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)

        level = logging.DEBUG if verbose else logging.INFO
        logger.setLevel(level)
        handler.setLevel(level)
        logger.addHandler(handler)
        self._logger = logger
