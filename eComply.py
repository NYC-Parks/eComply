import re
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

    def getAPIToken(self) -> str:
        url = (
            self._baseURL
            + "Authentication/ValidateUser?"
            + urllib.parse.urlencode(self._credential)
        )

        response = requests.post(url, headers=self._headers)

        if response.ok:
            result = response.json()
            # print(result)
            return result["token"]
        else:
            print(response.json())
            return ""

    def getHeaders(self) -> dict:
        token = self.getAPIToken()
        self._headers["Authorization"] = "Bearer " + token
        return self._headers

    def verifyToken(self, token: str):
        url = self._baseURL + "Authentication/AuthenticateToken?token=" + token
        print(url)
        response = requests.post(url, headers=self._headers)
        result = response.json()
        print(result)

    def getContracts(self) -> list:
        url = self._baseURL + "Contracts/ExportContracts"
        response = requests.get(url, headers=self.getHeaders())

        if response.ok:
            result = response.json()
            return result["data"]
        else:
            print(response.json())
            return []

    def postContracts(self, contracts: list) -> bool:
        url = self._baseURL + "Contracts/ImportContracts"
        response = requests.post(url, headers=self.getHeaders(), json=contracts)

        if not response.ok:
            raise Exception(response)

        response = requests.get(url, headers=self._headers)

        if not response.ok:
            raise Exception(response)

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

    class Domain:
        domainName: str
        code: str
        value: str

    def postDomainValues(self, domains: list[Domain]) -> bool:
        url = self._baseURL + "Catalog/ImportDomainNames"
        response = requests.post(url, headers=self.getHeaders(), json=domains)

        if not response.ok:
            raise Exception(response)

        response = requests.get(url, headers=self._headers)

        if not response.ok:
            raise Exception(response)

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

    def getWorkOrders(self) -> list:
        url = self._baseURL + "Contracts/ExportWorkOrders"
        response = requests.get(url, headers=self.getHeaders())

        if response.ok:
            result = response.json()
            return result["data"]
        else:
            print(response.json())
            return []

    def postWorkOrders(self, workOrders: list):
        url = self._baseURL + "Contracts/ImportWorkOrders"
        response = requests.post(url, headers=self.getHeaders(), json=workOrders)

        if not response.ok:
            raise Exception(response)

        response = requests.get(url, headers=self._headers)

        if not response.ok:
            raise Exception(response)

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

    def getWorkOrderLineItems(self) -> list:
        url = self._baseURL + "Contracts/ExportWorkOrderLineItems"
        response = requests.get(url, headers=self.getHeaders())

        if response.ok:
            result = response.json()
            return result["data"]
        else:
            print(response.json())
            return []
