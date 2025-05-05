# eComply SasS API Module

## Overview

The `eComply` module is designed to facilitate data replication and integration with the eComply REST API. It provides functionality to interact with various endpoints of the eComply system, including fetching and/or posting contracts, work orders, work order line items, and domain values.

## Features

- Fetch contracts, work orders, and work order line items from the eComply REST API.
- Post contracts, work orders, and domain values to the eComply REST API.
- Automatic schema validation and serialization of data.
- Conversion of date fields to epoch format for consistency.
- Token-based authentication with automatic token management.

## Usage

### Initialization

To use the `API` class, initialize it with the base URL, username, and password:

```python
from eComply import API

api = API(
    url="https://nycparks-stage.ecomply.us/WebAPI",
    username="your-username",
    password="your-password"
)
```

### Fetching Data

#### Fetch Contracts
```python
from datetime import datetime

contracts = api.get_contracts(fromDate=datetime(2023, 1, 1))
print(contracts)
```

#### Fetch Work Orders
```python
work_orders = api.get_work_orders(fromDate=datetime(2023, 1, 1))
print(work_orders)
```

#### Fetch Work Order Line Items
```python
line_items = api.get_work_order_line_items(fromDate=datetime(2023, 1, 1))
print(line_items)
```

### Posting Data

#### Post Contracts
```python
api.post_contracts(contracts)
```

#### Post Work Orders
```python
api.post_work_orders(work_orders)
```

#### Post Domain Values
```python
api.post_domain_values(domains)
```

## Logging

The module uses Python's built-in logging library. To enable logging, configure the logger in your application:

```python
import logging

logging.basicConfig(level=logging.DEBUG)
```

## Error Handling

The module raises exceptions for HTTP errors and schema validation issues. Ensure to wrap API calls in try-except blocks to handle errors gracefully.

```python
try:
    contracts = api.get_contracts(fromDate=datetime(2023, 1, 1))
except Exception as e:
    print(f"Error: {e}")
```

## License

This module is licensed under the MIT License. See the LICENSE file for details.