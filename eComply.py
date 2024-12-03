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
            + "Authentication/ValidateUser?"
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
            return result["data"]
        else:
            raise Exception(response.json())

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

    def getContracts(self) -> list:
        url = self._baseURL + "Contracts/ExportContracts"
        return self.__getEntities(url)

    class Contract:
        objectId: int
        codedValue: int
        contractName: str
        contractType: str
        contractStatus: str
        borough: str
        fundingSource: str
        projectManager: str
        contractor: str
        awardAmount: int
        awardDate: datetime
        orderToWorkDate: datetime
        specifiedCompletionDate: datetime
        anticipatedCompletionDate: datetime
        createdDate: datetime
        createdByName: str
        createdBYERN: str
        updatedDate: datetime
        updatedByName: str
        updatedByERN: str
        closedDate: datetime
        closedByName: str
        closedByERN: str
        cancelDate: datetime
        cancelByName: str
        cancelByERN: str
        cancelReason: str
        closedBySystem: int

    def postContracts(self, contracts: list[Contract]) -> bool:
        url = self._baseURL + "Contracts/ImportContracts"
        return self.__postEntities(url, contracts)

    class Domain:
        domainName: str
        code: str
        value: str

    def postDomainValues(self, domains: list[Domain]) -> bool:
        url = self._baseURL + "Catalog/ImportDomainNames"
        return self.__postEntities(url, domains)

    def getWorkOrders(self) -> list:
        url = self._baseURL + "Contracts/ExportWorkOrders"
        return self.__getEntities(url)

    class WorkOrder:
        objectId: int
        workOrderGlobalId: str
        contract: int
        borough: int
        communityBoard: int
        status: int
        cityCouncil: int
        recSpecies: int
        plantingSpaceId: int
        plantingSpaceGlobalId: str
        project: int
        projStartDate: datetime
        buildingNumber: str
        streetName: str
        onStreetSite: str
        location: str
        crossStreet1: str
        crossStreet2: str
        fundingSource: str
        actualFinishDate: datetime
        createdDate: datetime
        createdByName: str
        createdBYERN: str
        updatedDate: datetime
        updatedByName: str
        updatedByERN: str
        closedDate: datetime
        closedByName: str
        closedByERN: str
        cancelDate: datetime
        cancelByName: str
        cancelByERN: str
        cancelReason: str
        closedBySystem: int
        type: int
        parkName: str
        parkZone: str
        woEntity: int
        stateAssembly: int
        gispropnum: str

    def postWorkOrders(self, workOrders: list[WorkOrder]) -> bool:
        url = self._baseURL + "Contracts/ImportWorkOrders"
        return self.__postEntities(url, workOrders)

    def getWorkOrderLineItems(self) -> list:
        url = self._baseURL + "Contracts/ExportWorkOrderLineItems"
        return self.__getEntities(url)
