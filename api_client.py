from urllib.request import urlopen, Request
from urllib.parse import urlencode
import json
from config import ACCESS_TOKEN, API_VERSION, BASE_URL


class VKAPIError(Exception):
    def __init__(self, error_data):
        self.error_code = error_data.get('error_code')
        self.error_msg = error_data.get('error_msg')
        self.request_params = error_data.get('request_params')
        super().__init__(f"VK API Error {self.error_code}: {self.error_msg}")


def make_request(method_name: str, params: dict):
    params['v'] = API_VERSION
    params['access_token'] = ACCESS_TOKEN

    query_string = urlencode(params)
    url = f"{BASE_URL}{method_name}?{query_string}"

    try:
        http_req = Request(url)
        with urlopen(http_req, timeout=10) as response:  # timeout 10 секунд
            response_body = response.read().decode('utf-8')
            data = json.loads(response_body)
    except json.JSONDecodeError as e:
        raise ValueError(f"Ошибка декодирования JSON: {e}\nТело ответа (начало): {response_body[:500]}") from e
    except Exception as e:
        raise ConnectionError(f"Ошибка сетевого запроса для {url}: {e}") from e

    if 'error' in data:
        raise VKAPIError(data['error'])
    return data.get('response')
