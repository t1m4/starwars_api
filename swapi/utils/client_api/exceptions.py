class ClientAPIException(Exception):
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.error_message = message

    def __str__(self):
        return "{} {}".format(self.status_code, self.error_message)
