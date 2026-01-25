import requests
import backend.my_logger

API_URL = "http://127.0.0.1:8000"

class APIClient:
    def __init__(self, fn):
        self._endpoint = fn
        self.logger = backend.my_logger.config_logger(name="API Data")
        self._data = None

    def get_data(self):
        response = None
        try:
            response = requests.get(f"{API_URL}/{self._endpoint}", timeout=30)
            response.raise_for_status()
            self._data = response.json()

        except requests.exceptions.HTTPError:
            self.logger.error(f"{response.status_code} - {response.reason}")
            self._data = []

        return self._data


    def post_data(self, data):
        response = None
        try:
            response = requests.post(
                f"{API_URL}/{self._endpoint}",
                json = data.to_dict(orient="records"),
                timeout = 30
            )

            response.raise_for_status()
            self.logger.info("Expenses saved successfully")

        except requests.exceptions.HTTPError as e:
            raise RuntimeError(response.json().get("detail", "API Error"))


        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Backend not reachable - {e}")