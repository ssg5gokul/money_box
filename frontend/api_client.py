import requests
from frontend.bootstrap import setup_project_root

setup_project_root()

import backend.my_logger
import os
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("API_URL")

class APIClient:
    def __init__(self, fn):
        self._endpoint = fn
        self.logger = backend.my_logger.config_logger(name="API Data")
        self._data = []

    def get_data(self):
        try:
            response = requests.get(f"{API_URL}/{self._endpoint}", timeout=5)
            response.raise_for_status()
            self._data = response.json()
            return self._data

        except requests.exceptions.HTTPError as HttpErr:
            resp = HttpErr.response

            status = resp.status_code if resp else "Unknown"
            reason = resp.reason if resp else "No response"

            self.logger.error(f"{status} - {reason}")

            detail = "API Error"
            if resp is not None:
                try:
                    detail = resp.json().get("detail", detail)
                except ValueError:
                    pass

            raise RuntimeError(detail)

        except requests.RequestException as RequestErr:
            self.logger.error(f"Backend not reachable - {RequestErr}")
            raise TimeoutError(f"Backend not reachable - {RequestErr}")


    def post_data(self, data):
        try:
            response = requests.post(
                f"{API_URL}/{self._endpoint}",
                json = data.to_dict(orient="records"),
                timeout = 5
            )

            response.raise_for_status()
            self.logger.info("Records saved successfully")

        except requests.exceptions.HTTPError as HTTPErr:
            resp = HTTPErr.response

            status = resp.status_code if resp else "Unknown"
            reason = resp.reason if resp else "No response"

            self.logger.error(f"{status} - {reason}")

            detail = "API Error"
            if resp is not None:
                try:
                    detail = resp.json().get("detail", detail)
                except ValueError:
                    pass

            raise ConnectionError(detail)


        except requests.exceptions.RequestException as RequestErr:
            self.logger(f"Backend not reachable - {RequestErr}")
            raise RuntimeError(f"Backend not reachable - {RequestErr}")


    def get_user(self, user_id=None):
        try:
            headers = {}
            if user_id:
                headers["x-user-id"] = user_id
            response = requests.get(f"{API_URL}/{self._endpoint}", headers=headers, timeout=10)
            response.raise_for_status()
            self._data = response.json()
            return self._data

        except requests.exceptions.HTTPError as HttpErr:
            resp = HttpErr.response

            status = resp.status_code if resp else "Unknown"
            reason = resp.reason if resp else "No response"

            self.logger.error(f"{status} - {reason}")

            detail = "API Error"
            if resp is not None:
                try:
                    detail = resp.json().get("detail", detail)
                except ValueError:
                    pass

            raise RuntimeError(detail)

        except requests.RequestException as RequestErr:
            self.logger.error(f"Backend not reachable - {RequestErr}")
            raise TimeoutError(f"Backend not reachable - {RequestErr}")
