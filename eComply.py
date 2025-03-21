from datetime import datetime
from json import dumps
from typing import Any
from pandas import DataFrame
from requests import Response, post, get
from urllib import parse


class eComply:
    _url: str
    _credential: dict
    _token: str | None = None
    _headers: dict = {
        "Authorization": "",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    def __init__(
        self,
        url: str,
        username: str,
        password: str,
    ) -> None:
        self._url = url
        self._credential = {"username": username, "password": password}

    def __get_api_token(self) -> str:
        url = (
            self._url
            + "/Authentication/ValidateUser?"
            + parse.urlencode(self._credential)
        )
        response: Response = post(url, headers=self._headers)

        result: dict = response.json()
        if response.ok:
            return result["token"]
        else:
            raise Exception(result)

    def __get_headers(self) -> dict:
        if self._token is None:
            self._token = self.__get_api_token()
        self._headers["Authorization"] = f"Bearer {self._token}"
        return self._headers

    def __get_entities(self, url: str, params: dict) -> list:
        response: Response = get(
            url=url,
            headers=self.__get_headers(),
            params=params,
        )

        return list(self.__response_handler(response))

    def __post_entities(self, url: str, data: Any) -> dict[str, Any]:
        response: Response = post(
            url=url,
            headers=self.__get_headers(),
            data=self.__to_json(data),
        )

        if not response.ok:
            raise Exception(response.json())

        response: Response = get(
            url=url,
            headers=self._headers,
        )

        return dict(self.__response_handler(response))

    def __response_handler(self, response: Response) -> dict[str, Any] | list:
        result: dict = response.json()
        if not response.ok:
            raise Exception(result)

        if result["success"]:
            return result["data"]
        else:
            raise Exception(result)

    def __to_json(self, obj: Any) -> str:
        if isinstance(obj, DataFrame):
            return obj.to_json(orient="records", date_format="iso")

        return dumps(obj)

    # def __verifyToken(self, token: str):
    #     url = self._baseURL + "Authentication/AuthenticateToken?token=" + token
    #     print(url)
    #     response = requests.post(url, headers=self._headers)
    #     result = response.json()
    #     print(result)

    def get_contracts(self, fromDate: datetime) -> list:
        url = f"{self._url}/Contracts/ExportContracts"
        return self.__get_entities(url, {fromDate: fromDate})

    def post_contracts(self, contracts: Any) -> dict:
        url = f"{self._url}/Contracts/ImportContracts"
        return self.__post_entities(url, contracts)

    def post_domain_values(self, domains: Any) -> dict:
        url = f"{self._url}/Catalog/ImportDomainNames"
        return self.__post_entities(url, domains)

    def get_work_orders(self, fromDate: datetime) -> list:
        url = f"{self._url}/Contracts/ExportWorkOrders"
        return self.__get_entities(url, {fromDate: fromDate})

    def post_work_orders(self, workOrders: Any) -> dict:
        url = f"{self._url}/Contracts/ImportWorkOrders"
        return self.__post_entities(url, workOrders)

    def get_work_order_line_items(self, fromDate: datetime) -> list:
        url = f"{self._url}/Contracts/ExportWorkOrderLineItems"
        return self.__get_entities(url, {fromDate: fromDate})
