import re

def test_latest_endpoint_success(client):
    res = client.request("GET", "/latest")
    latency = res["latency_ms"]
    
    if res["error"]:
        return {"name": "GET /latest - Success", "status": "FAIL", "latency_ms": latency, "details": f"Network/Timeout Error: {res['error']}"}
    
    if res["status_code"] != 200:
        return {"name": "GET /latest - Success", "status": "FAIL", "latency_ms": latency, "details": f"Expected HTTP 200, got {res['status_code']}"}
        
    data = res["json"]
    if not data:
        return {"name": "GET /latest - Success", "status": "FAIL", "latency_ms": latency, "details": "Response not JSON or invalid format"}
        
    # Schema check
    required_keys = {"amount", "base", "date", "rates"}
    missing_keys = required_keys - data.keys()
    if missing_keys:
        return {"name": "GET /latest - Success", "status": "FAIL", "latency_ms": latency, "details": f"Missing keys in schema: {missing_keys}"}
        
    if not isinstance(data["amount"], (int, float)):
        return {"name": "GET /latest - Success", "status": "FAIL", "latency_ms": latency, "details": f"amount type is {type(data['amount'])}, expected float/int"}
    if not isinstance(data["base"], str) or data["base"] != "EUR":
        return {"name": "GET /latest - Success", "status": "FAIL", "latency_ms": latency, "details": f"base currency is {data['base']}, expected 'EUR'"}
    if not isinstance(data["date"], str) or not re.match(r"^\d{4}-\d{2}-\d{2}$", data["date"]):
        return {"name": "GET /latest - Success", "status": "FAIL", "latency_ms": latency, "details": f"date is {data['date']}, expected YYYY-MM-DD format"}
    if not isinstance(data["rates"], dict) or len(data["rates"]) == 0:
        return {"name": "GET /latest - Success", "status": "FAIL", "latency_ms": latency, "details": "rates must be a non-empty dictionary"}
        
    return {"name": "GET /latest - Success", "status": "PASS", "latency_ms": latency, "details": "Schema and contract validation passed successfully."}

def test_latest_with_base_usd(client):
    res = client.request("GET", "/latest", params={"from": "USD"})
    latency = res["latency_ms"]
    
    if res["error"]:
        return {"name": "GET /latest?from=USD", "status": "FAIL", "latency_ms": latency, "details": f"Network/Timeout Error: {res['error']}"}
        
    if res["status_code"] != 200:
        return {"name": "GET /latest?from=USD", "status": "FAIL", "latency_ms": latency, "details": f"Expected HTTP 200, got {res['status_code']}"}
        
    data = res["json"]
    if not data:
        return {"name": "GET /latest?from=USD", "status": "FAIL", "latency_ms": latency, "details": "Response not JSON"}
        
    if data.get("base") != "USD":
        return {"name": "GET /latest?from=USD", "status": "FAIL", "latency_ms": latency, "details": f"base is {data.get('base')}, expected 'USD'"}
        
    rates = data.get("rates", {})
    if "USD" in rates:
        return {"name": "GET /latest?from=USD", "status": "FAIL", "latency_ms": latency, "details": "rates dictionary should not contain the base currency 'USD'"}
    if "EUR" not in rates:
        return {"name": "GET /latest?from=USD", "status": "FAIL", "latency_ms": latency, "details": "rates dictionary should contain 'EUR' when base is 'USD'"}
        
    return {"name": "GET /latest?from=USD", "status": "PASS", "latency_ms": latency, "details": "Base currency filtering passed successfully."}

def test_latest_with_filter_currencies(client):
    res = client.request("GET", "/latest", params={"from": "USD", "to": "EUR,GBP"})
    latency = res["latency_ms"]
    
    if res["error"]:
        return {"name": "GET /latest?from=USD&to=EUR,GBP", "status": "FAIL", "latency_ms": latency, "details": f"Network/Timeout Error: {res['error']}"}
        
    if res["status_code"] != 200:
        return {"name": "GET /latest?from=USD&to=EUR,GBP", "status": "FAIL", "latency_ms": latency, "details": f"Expected HTTP 200, got {res['status_code']}"}
        
    data = res["json"]
    if not data:
        return {"name": "GET /latest?from=USD&to=EUR,GBP", "status": "FAIL", "latency_ms": latency, "details": "Response not JSON"}
        
    rates = data.get("rates", {})
    expected_rates = {"EUR", "GBP"}
    actual_rates = set(rates.keys())
    if actual_rates != expected_rates:
        return {"name": "GET /latest?from=USD&to=EUR,GBP", "status": "FAIL", "latency_ms": latency, "details": f"Expected rates {expected_rates}, got {actual_rates}"}
        
    for currency, val in rates.items():
        if not isinstance(val, (int, float)):
            return {"name": "GET /latest?from=USD&to=EUR,GBP", "status": "FAIL", "latency_ms": latency, "details": f"Rate for {currency} is {type(val)}, expected float/int"}
            
    return {"name": "GET /latest?from=USD&to=EUR,GBP", "status": "PASS", "latency_ms": latency, "details": "Target currency filtering passed successfully."}

def test_historical_date_success(client):
    res = client.request("GET", "/2020-01-01")
    latency = res["latency_ms"]
    
    if res["error"]:
        return {"name": "GET /2020-01-01", "status": "FAIL", "latency_ms": latency, "details": f"Network/Timeout Error: {res['error']}"}
        
    if res["status_code"] != 200:
        return {"name": "GET /2020-01-01", "status": "FAIL", "latency_ms": latency, "details": f"Expected HTTP 200, got {res['status_code']}"}
        
    data = res["json"]
    if not data:
        return {"name": "GET /2020-01-01", "status": "FAIL", "latency_ms": latency, "details": "Response not JSON"}
        
    required_keys = {"amount", "base", "date", "rates"}
    missing_keys = required_keys - data.keys()
    if missing_keys:
        return {"name": "GET /2020-01-01", "status": "FAIL", "latency_ms": latency, "details": f"Missing keys in schema: {missing_keys}"}
        
    if not isinstance(data["date"], str) or not re.match(r"^\d{4}-\d{2}-\d{2}$", data["date"]):
        return {"name": "GET /2020-01-01", "status": "FAIL", "latency_ms": latency, "details": f"date is {data['date']}, expected YYYY-MM-DD format"}
        
    return {"name": "GET /2020-01-01", "status": "PASS", "latency_ms": latency, "details": f"Historical rates for 2020-01-01 retrieved. Real date resolved is {data['date']}"}

def test_currencies_list(client):
    res = client.request("GET", "/currencies")
    latency = res["latency_ms"]
    
    if res["error"]:
        return {"name": "GET /currencies", "status": "FAIL", "latency_ms": latency, "details": f"Network/Timeout Error: {res['error']}"}
        
    if res["status_code"] != 200:
        return {"name": "GET /currencies", "status": "FAIL", "latency_ms": latency, "details": f"Expected HTTP 200, got {res['status_code']}"}
        
    data = res["json"]
    if not isinstance(data, dict):
        return {"name": "GET /currencies", "status": "FAIL", "latency_ms": latency, "details": "Expected currency mapping to be a JSON object (dict)"}
        
    major_currencies = {"USD", "EUR", "GBP", "JPY", "CAD"}
    missing_majors = major_currencies - data.keys()
    if missing_majors:
        return {"name": "GET /currencies", "status": "FAIL", "latency_ms": latency, "details": f"Missing major currencies in list: {missing_majors}"}
        
    return {"name": "GET /currencies", "status": "PASS", "latency_ms": latency, "details": f"Currencies list retrieved successfully. Total currencies: {len(data)}"}

def test_invalid_currency_code_error(client):
    res = client.request("GET", "/latest", params={"from": "INVALID"})
    latency = res["latency_ms"]
    
    if res["error"]:
        return {"name": "GET /latest?from=INVALID", "status": "FAIL", "latency_ms": latency, "details": f"Network/Timeout Error: {res['error']}"}
        
    if res["status_code"] != 404:
        return {"name": "GET /latest?from=INVALID", "status": "FAIL", "latency_ms": latency, "details": f"Expected HTTP 404 for invalid base, got {res['status_code']}"}
        
    return {"name": "GET /latest?from=INVALID", "status": "PASS", "latency_ms": latency, "details": "Error handling validation: received expected 404 status."}

def test_invalid_endpoint_error(client):
    res = client.request("GET", "/invalid_route_does_not_exist")
    latency = res["latency_ms"]
    
    if res["error"]:
        return {"name": "GET /invalid_route_does_not_exist", "status": "FAIL", "latency_ms": latency, "details": f"Network/Timeout Error: {res['error']}"}
        
    if res["status_code"] != 404:
        return {"name": "GET /invalid_route_does_not_exist", "status": "FAIL", "latency_ms": latency, "details": f"Expected HTTP 404 for non-existent endpoint, got {res['status_code']}"}
        
    return {"name": "GET /invalid_route_does_not_exist", "status": "PASS", "latency_ms": latency, "details": "Error handling validation: received expected 404 status for invalid endpoint."}
