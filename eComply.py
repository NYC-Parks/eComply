import requests
import urllib.parse


class eComply:
    url: str
    credential: dict
    headers: dict = {
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
        self.url = url
        self.credential = {"username": username, "password": password}

    def getAPIToken(self) -> str:
        url = (
            self.url
            + "Authentication/ValidateUser?"
            + urllib.parse.urlencode(self.credential)
        )
        response = requests.post(url, headers=self.headers)

        if response.ok:
            result = response.json()
            # print(result)
            return result["token"]
        else:
            print(response.json())
            return ""

    def verifyToken(self, token: str):
        url = self.url + "Authentication/AuthenticateToken?token=" + token
        print(url)
        response = requests.post(url, headers=self.headers)
        result = response.json()
        print(result)

    def getContracts(self):
        token = self.getAPIToken()
        # print(self.verifyToken(token))
        self.headers["Authorization"] = "Bearer " + token
        url = self.url + "Contracts/ExportContracts"
        #         print(url)
        response = requests.get(url, headers=self.headers)

        if response.ok:
            result = response.json()
            return result["data"]
        else:
            print(response.json())
