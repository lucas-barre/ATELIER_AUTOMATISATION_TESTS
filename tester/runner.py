import time
from datetime import datetime
from .client import APIClient
from .tests import (
    test_latest_endpoint_success,
    test_latest_with_base_usd,
    test_latest_with_filter_currencies,
    test_historical_date_success,
    test_currencies_list,
    test_invalid_currency_code_error,
    test_invalid_endpoint_error
)

def run_all_tests():
    client = APIClient()
    
    test_functions = [
        test_latest_endpoint_success,
        test_latest_with_base_usd,
        test_latest_with_filter_currencies,
        test_historical_date_success,
        test_currencies_list,
        test_invalid_currency_code_error,
        test_invalid_endpoint_error
    ]
    
    results = []
    latencies = []
    passed = 0
    failed = 0
    
    timestamp = datetime.utcnow().isoformat() + "Z"
    
    for test_fn in test_functions:
        res = test_fn(client)
        results.append(res)
        latencies.append(res["latency_ms"])
        if res["status"] == "PASS":
            passed += 1
        else:
            failed += 1
        
        # Friendly rate-limiting precaution
        time.sleep(0.2)
        
    total_tests = len(results)
    error_rate = failed / total_tests if total_tests > 0 else 0
    availability = passed / total_tests if total_tests > 0 else 0
    
    # QoS latencies calculation
    latencies.sort()
    avg_latency = sum(latencies) / total_tests if total_tests > 0 else 0
    if total_tests > 0:
        p95_idx = max(0, int(len(latencies) * 0.95) - 1)
        p95_latency = latencies[p95_idx]
    else:
        p95_latency = 0
        
    return {
        "api": "Frankfurter",
        "timestamp": timestamp,
        "summary": {
            "total": total_tests,
            "passed": passed,
            "failed": failed,
            "error_rate": error_rate,
            "availability": availability,
            "latency_ms_avg": avg_latency,
            "latency_ms_p95": p95_latency
        },
        "tests": results
    }
