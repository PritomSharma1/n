

class TempClient:
    _instance = None

    

    def __init__(self, phone_number=None, client=None, response=None, two_factor_password=None):

        self._phone_number = phone_number
        self._client = client
        self._response = response
        self._two_factor_password = two_factor_password

    @property
    def phone_number(self):
        return self._phone_number

    @phone_number.setter
    def phone_number(self, phone_number):
        self._phone_number = phone_number

    @property
    def client(self):
        return self._client

    @client.setter
    def client(self, client):
        self._client = client

    @property
    def response(self):
        return self._response

    @response.setter
    def response(self, response):
        self._response = response

    @property
    def two_factor_password(self):
        return self._two_factor_password

    @two_factor_password.setter
    def two_factor_password(self, two_factor_password):
        self._two_factor_password = two_factor_password

    def content(self):
        result = {
            'phone_number': self._phone_number,
            'code': self.response,
            'password': self.two_factor_password
        }

        return result
    
    def __str__(self) -> str:
        return str(self.content())


