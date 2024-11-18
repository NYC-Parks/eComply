import requests
import urllib.parse


class eComply:
    _url: str
    _credential: dict
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

    def getAPIToken(self) -> str:
        url = (
            self._url
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

    def verifyToken(self, token: str):
        url = self._url + "Authentication/AuthenticateToken?token=" + token
        print(url)
        response = requests.post(url, headers=self._headers)
        result = response.json()
        print(result)

    def getContracts(self):
        token = self.getAPIToken()
        # print(self.verifyToken(token))
        self._headers["Authorization"] = "Bearer " + token
        url = self._url + "Contracts/ExportContracts"
        # print(url)
        response = requests.get(url, headers=self._headers)

        if response.ok:
            result = response.json()
            return result["data"]
        else:
            print(response.json())

    def postDomainValues(self, domain):
        token = self.getAPIToken()
        self._headers["Authorization"] = "Bearer " + token
        url = self._url + "Catalog/ImportDomainNames"

        data = []
        for value in domain["codedValues"]:
            data.append(
                {
                    "domainName": domain["name"],
                    "code": str(value["code"]),
                    "value": value["name"],
                }
            )

        response = requests.post(url, headers=self._headers, json=data)
        print(response.json())
        if response.ok:
            response = requests.get(url, headers=self._headers)
            print(response.json())
