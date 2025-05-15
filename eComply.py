from datetime import datetime
from logging import getLogger
from typing import Any
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
        response.raise_for_status()
        return response.json()

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

    def _get_entities(self, url: str, params: dict, schema: str) -> DataFrame:
        response: Response = get(
            url=url,
            headers=self._get_headers(),
            params=params,
        )
        response.raise_for_status()
        entities = list(self._response_handler(response))

        definition = self._get_schema_definition(schema)
        self._logger.debug(f"{schema} Schema Definition: {definition}")

        entities = self._serialize(entities, definition)
        self._convert_dates_to_epoch(entities)

        return entities

    def _get_schema_definition(
        self,
        name: str,
    ) -> dict[str, Any]:
        schemas = self._openapi_spec.get("components", {}).get("schemas", {})
        if name not in schemas:
            raise ValueError(f"Schema '{name}' not found in API specification")
        return schemas[name]

    def _serialize(self, entities: list, schema_definition: dict) -> DataFrame:
        schema = self._create_schema(schema_definition)
        self._logger.debug(f"Schema: {schema}")
        df = self._create_dataframe(entities, schema)
        self._logger.debug(f"Result: {df}")
        return df

    def _create_schema(
        self,
        schema_definition: dict[str, Any],
    ) -> dict[str, str]:
        dtype_dict = {}

        for name, details in schema_definition.get("properties", {}).items():
            dtype_dict[name] = self._type_to_dtype(
                details.get("type"),
                details.get("format"),
            )

        return dtype_dict

    def _type_to_dtype(
        self,
        type: str,
        format: str | None = None,
    ) -> str:
        type_mapping = {
            "string": "object",
            "integer": "int64",
            "number": "float64",
            "boolean": "bool",
            "array": "object",  # Arrays will be handled as Python objects
        }

        # Handle special formats
        if type == "string" and format == "date-time":
            return "datetime64[ns]"

        return type_mapping.get(type, "object")

    def _create_dataframe(
        self,
        data: list,
        dtype_dict: dict[str, str],
    ) -> DataFrame:
        df = DataFrame(data)

        for col, dtype in dtype_dict.items():
            if col in df.columns:
                try:
                    df[col] = df[col].astype(dtype)
                except (ValueError, TypeError) as e:
                    print(f"Warning: Could not convert column '{col}' to {dtype}: {e}")

        return df

    def _convert_dates_to_epoch(self, df: DataFrame) -> None:
        date_columns = df.select_dtypes(include=["datetime64[ns]"]).columns
        self._logger.debug(f"Date columns: {date_columns}")
        for col in date_columns:
            df[col] = df[col].astype("int64") // 10**9

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
        response: Response = post(
            url=url,
            headers=self._get_headers(),
            data=data,
        )
        response.raise_for_status()

        if not response.ok:
            raise Exception(response.json())

        return dict(self._response_handler(response))

    def _get_headers(self) -> dict:
        if self._token is None:
            self._token = self._get_api_token()
        self._headers["Authorization"] = f"Bearer {self._token}"
        return self._headers

    def _get_api_token(self) -> str:
        self._logger.debug(f"OpenAPI Specs: {self._openapi_spec}")
        result = self._authenticate()
        return result["token"]

    def _authenticate(self):
        url = f"{self._url}/Authentication/ValidateUser?{parse.urlencode(self._credential)}"
        response: Response = post(url, headers=self._headers)
        response.raise_for_status()
        return response.json()

    def _response_handler(self, response: Response) -> dict[str, Any] | list:
        result: dict = response.json()
        if not response.ok:
            raise Exception(result)

        if result["success"]:
            return result["data"]
        else:
            raise Exception(result)

    def _verifyToken(self, token: str):
        url = f"{self._url}Authentication/AuthenticateToken?token={self._token}"
        response = post(url, headers=self._headers)
        result = response.json()
        self._logger.debug(f"Token Verification: {result}")
