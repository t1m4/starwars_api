class CSVReaderException(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class EmptyPage(CSVReaderException):
    pass


class PageNotAnPositiveInteger(CSVReaderException):
    pass


class FileNotExist(CSVReaderException):
    pass
