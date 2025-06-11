from datetime import datetime
from json import dumps
from logging import getLogger
from typing import Any, Final
from pandas import DataFrame
from requests import Response, post, get
from urllib import parse


class API:
    _url: str
    _credential: dict
    _openapi_spec: dict
    _token: str | None = None
    _headers: dict = {
        "Authorization": "",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    _logger = getLogger("[ eComply ]")

    def __init__(
        self,
        url: str,
        username: str,
        password: str,
    ) -> None:
        self._url = url
        self._credential = {"username": username, "password": password}
        self._openapi_spec = self._get_swagger_specs()

    def _get_swagger_specs(self) -> dict:
        response = get(self._url + "/swagger/v1/swagger.json")
        return self._response_handler(response)

    def get_contracts(self, fromDate: datetime) -> DataFrame:
        return self._get_entities(
            f"{self._url}/Contracts/ExportContracts",
            {fromDate: fromDate},
            "ImportContractIntegrationModel",
        )

    def get_work_orders(self, fromDate: datetime) -> DataFrame:
        return self._get_entities(
            f"{self._url}/Contracts/ExportWorkOrders",
            {fromDate: fromDate},
            "WorkOrderIntegrationModel",
        )

    def get_work_order_line_items(self, fromDate: datetime) -> DataFrame:
        return self._get_entities(
            f"{self._url}/Contracts/ExportWorkOrderLineItems",
            {fromDate: fromDate},
            "WorkOrderLineItemIntegrationModel",
        )

    def _get_entities(self, url: str, params: dict, schema_name: str) -> DataFrame:
        self._logger.debug(
            f"Fetching entities from {url} with params: {params} and schema: {schema_name}"
        )
        response: Response = get(
            url=url,
            headers=self._get_headers(),
            params=params,
        )
        result = self._response_handler(response)

        if result["success"]:
            entities = list(result["data"])
        else:
            raise Exception(result)

        return self._deserialize(entities, schema_name)

    def _deserialize(self, entities: list[dict], schema_name: str) -> DataFrame:
        schema = self._create_schema(schema_name)
        self._logger.debug(f"Deserializing {entities}, using schema: {schema}")
        return self._create_dataframe(entities, schema)

    def _create_schema(
        self,
        name: str,
    ) -> dict[str, str]:
        schemas = self._openapi_spec["components"]["schemas"]
        if name not in schemas:
            raise ValueError(f"Schema '{name}' not found in API specification")

        schema_definition = schemas[name]
        type_mapping: Final = {
            "string": "object",
            "integer": "object",  # Must be nullable and json serializable
            "number": "object",  # Must be nullable and json serializable
            "boolean": "bool",
            "array": "object",  # Arrays will be handled as Python objects
        }
        dtype_dict = {}

        for name, details in schema_definition["properties"].items():
            if details["type"] == "string" and details.get("format") == "date-time":
                dtype_dict[name] = "datetime64[ns]"
            else:
                dtype_dict[name] = type_mapping[details["type"]]

        return dtype_dict

    def _create_dataframe(
        self,
        entities: list[dict],
        schema: dict[str, str],
    ) -> DataFrame:
        df = DataFrame(entities).astype(schema)
        df.columns = [col[0].upper() + col[1:] for col in df.columns]
        df.columns = [col[:-2] + "ID" if col.endswith("Id") else col for col in df.columns]
        df.columns = [col.upper() if col == "ObjectID" else col for col in df.columns]
        return df

    def post_contracts(self, contracts: Any) -> dict:
        url = f"{self._url}/Contracts/ImportContracts"
        return self._post_entities(url, contracts)

    def post_domain_values(self, domains: Any) -> dict:
        url = f"{self._url}/Catalog/ImportDomainNames"
        return self._post_entities(url, domains)

    def post_work_orders(self, workOrders: Any) -> dict:
        url = f"{self._url}/Contracts/ImportWorkOrders"
        return self._post_entities(url, workOrders)

    def _post_entities(self, url: str, data: Any) -> dict[str, Any]:
        data = self._serialize(data)
        self._logger.debug(f"Posting data to {url}: {data}")

        response: Response = post(
            url=url,
            headers=self._get_headers(),
            data=data,
        )
        result = self._response_handler(response)

        if result["success"]:
            return dict(result["data"])
        else:
            raise Exception(result)

    def _serialize(self, obj: Any) -> str:
        if isinstance(obj, DataFrame):
            for col in obj.select_dtypes(include=["datetime64[ns]"]).columns:
                obj[col] = obj[col].dt.strftime("%Y-%m-%dT%H:%M:%SZ")
            return obj.to_json(orient="records")
        else:
            return dumps(obj)

    def _get_headers(self) -> dict:
        if self._token is None:
            self._token = self._get_api_token()
        self._headers["Authorization"] = f"Bearer {self._token}"
        return self._headers

    def _get_api_token(self) -> str:
        self._logger.debug(f"OpenAPI Specs: {self._openapi_spec}")

        url = f"{self._url}/Authentication/ValidateUser?{parse.urlencode(self._credential)}"
        response: Response = post(url, headers=self._headers)
        result = self._response_handler(response)

        return result["token"]

    def _response_handler(self, response: Response) -> dict[str, Any]:
        response.raise_for_status()

        result = response.json()
        if not response.ok:
            raise Exception(result)

        return result

    # def _verifyToken(self, token: str):
    #     url = f"{self._url}Authentication/AuthenticateToken?token={self._token}"
    #     response = post(url, headers=self._headers)
    #     result = response.json()
    #     self._logger.debug(f"Token Verification: {result}")
