from datetime import datetime
import requests
import urllib.parse


class eComply:
    _baseURL: str
    _credential: dict
    _headers: dict = {
        "Authorization": "",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    def __init__(
        self,
        baseURL: str,
        username: str,
        password: str,
    ) -> None:
        self._baseURL = baseURL
        self._credential = {"username": username, "password": password}

    def __getAPIToken(self) -> str:
        url = (
            self._baseURL
            + "/Authentication/ValidateUser?"
            + urllib.parse.urlencode(self._credential)
        )

        response = requests.post(url, headers=self._headers)

        if response.ok:
            result = response.json()
            # print(result)
            return result["token"]
        else:
            raise Exception(response.json())

    def __getHeaders(self) -> dict:
        token = self.__getAPIToken()
        self._headers["Authorization"] = "Bearer " + token
        return self._headers

    def __getEntities(self, url: str) -> list:
        response = requests.get(url, headers=self.__getHeaders())

        if response.ok:
            result = response.json()
            if result["success"]:
                return result["data"]
            else:
                raise Exception(result["message"])
        else:
            raise Exception(response.json()["message"])

    def __postEntities(self, url: str, entities: list) -> bool:
        response = requests.post(url, headers=self.__getHeaders(), json=entities)

        if not response.ok:
            raise Exception(response.json())

        response = requests.get(url, headers=self._headers)

        if not response.ok:
            raise Exception(response.json())

        result = response.json()
        if result["success"]:
            print(
                {
                    "success": result["success"],
                    "processedResults": result["data"]["processedResults"],
                    "totalProcessed": result["data"]["totalProcessed"],
                    "totalWithErrors": result["data"]["totalWithErrors"],
                    "totalUpdated": result["data"]["totalUpdated"],
                    "totalCreated": result["data"]["totalCreated"],
                }
            )
        else:
            print(
                {
                    "success": result["success"],
                    "message": result["message"],
                }
            )

        return result["success"]

    # def __verifyToken(self, token: str):
    #     url = self._baseURL + "Authentication/AuthenticateToken?token=" + token
    #     print(url)
    #     response = requests.post(url, headers=self._headers)
    #     result = response.json()
    #     print(result)

    def getContracts(self, fromDate: datetime) -> list:
        url = f"{self._baseURL}/Contracts/ExportContracts?fromDate={fromDate}"
        return self.__getEntities(url)

    def postContracts(self, contracts: list) -> bool:
        url = f"{self._baseURL}/Contracts/ImportContracts"
        return self.__postEntities(url, contracts)

    def postDomainValues(self, domains: list) -> bool:
        url = f"{self._baseURL}/Catalog/ImportDomainNames"
        return self.__postEntities(url, domains)

    def getWorkOrders(self, fromDate: datetime) -> list:
        url = f"{self._baseURL}/Contracts/ExportWorkOrders?fromDate={fromDate}"
        return self.__getEntities(url)

    def postWorkOrders(self, workOrders: list) -> bool:
        url = f"{self._baseURL}/Contracts/ImportWorkOrders"
        return self.__postEntities(url, workOrders)

    def getWorkOrderLineItems(self, fromDate: datetime) -> list:
        url = f"{self._baseURL}/Contracts/ExportWorkOrderLineItems?fromDate={fromDate}"
        return self.__getEntities(url)
