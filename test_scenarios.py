"""
Automated Test Suite for Green Minds AI Assistant
Executes multiple diverse agricultural scenarios and edge cases.
"""

import json
import urllib.request
import urllib.error
import time
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

BASE_URL = "http://127.0.0.1:5000"

def log_test(title, passed, details=""):
    status = "[PASS]" if passed else "[FAIL]"
    print(f"\n{'='*70}\n{title} -> {status}\n{'='*70}")
    if details:
        print(details)

def run_scenario(name, payload, expected_status=200):
    print(f"\n--- Testing Scenario: {name} ---")
    req = urllib.request.Request(
        f"{BASE_URL}/api/advice",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    
    start_time = time.time()
    try:
        with urllib.request.urlopen(req, timeout=45) as response:
            status = response.status
            body = json.loads(response.read().decode("utf-8"))
            elapsed = time.time() - start_time
            
            success = body.get("success", False)
            advice = body.get("advice", "")
            farmer_name = body.get("farmerName", "")
            
            has_sections = any(sec in advice for sec in ["Crop care", "Water management", "Soil", "Weather", "risks", "Next steps", "advice"])
            
            print(f"Status Code: {status}")
            print(f"Response Time: {elapsed:.2f}s")
            print(f"Farmer Name Returned: {farmer_name}")
            print(f"Advice Length: {len(advice)} characters")
            print("\nPreview of AI Guidance:")
            print(advice[:400] + "...\n")
            
            passed = (status == expected_status) and success and has_sections
            log_test(name, passed, f"Response valid with {len(advice)} chars of advice in {elapsed:.2f}s")
            return passed, advice
            
    except urllib.error.HTTPError as e:
        elapsed = time.time() - start_time
        err_body = e.read().decode("utf-8")
        print(f"HTTP Error {e.code}: {err_body}")
        passed = (e.code == expected_status)
        log_test(name, passed, f"Expected {expected_status}, received {e.code}")
        return passed, err_body
    except Exception as e:
        print(f"Exception encountered: {str(e)}")
        log_test(name, False, str(e))
        return False, str(e)


def run_all_tests():
    print("=== STARTING GREEN MINDS EXTENSIVE TEST SUITE ===")
    results = []

    # 1. Health check test
    print("\n--- Testing 1: Health Check Endpoint (GET /) ---")
    try:
        with urllib.request.urlopen(f"{BASE_URL}/", timeout=10) as res:
            data = json.loads(res.read().decode("utf-8"))
            passed = data.get("status") == "online" and data.get("apiKeyConfigured") is True
            log_test("Health Check Endpoint", passed, f"Service: {data.get('service')}, Key Configured: {data.get('apiKeyConfigured')}")
            results.append(("Health Check Endpoint", passed))
    except Exception as e:
        log_test("Health Check Endpoint", False, str(e))
        results.append(("Health Check Endpoint", False))

    # Scenario 1: Coastal Monsoon Paddy
    s1_payload = {
        "name": "Lakshmi Devi",
        "state": "Andhra Pradesh",
        "district": "East Godavari",
        "crop": "Rice / Paddy",
        "soilType": "Alluvial Soil",
        "weatherCondition": "Rainy / Monsoon"
    }
    p1, _ = run_scenario("Scenario 1: Coastal Monsoon Rice (Lakshmi Devi, AP)", s1_payload)
    results.append(("Scenario 1: Monsoon Rice", p1))

    # Scenario 2: Semi-Arid Black Soil Cotton
    s2_payload = {
        "name": "Vijay Shinde",
        "state": "Maharashtra",
        "district": "Yavatmal",
        "crop": "Cotton",
        "soilType": "Black Soil / Regur",
        "weatherCondition": "Hot & Dry"
    }
    p2, _ = run_scenario("Scenario 2: Hot & Dry Cotton in Black Soil (Vijay Shinde, MH)", s2_payload)
    results.append(("Scenario 2: Hot & Dry Cotton", p2))

    # Scenario 3: Cold Winter Mustard
    s3_payload = {
        "name": "Gurpreet Singh",
        "state": "Punjab",
        "district": "Ludhiana",
        "crop": "Mustard",
        "soilType": "Loamy Soil",
        "weatherCondition": "Cold / Winter Frost"
    }
    p3, _ = run_scenario("Scenario 3: Winter Frost Mustard (Gurpreet Singh, Punjab)", s3_payload)
    results.append(("Scenario 3: Winter Frost Mustard", p3))

    # Scenario 4: Edge Case - Empty Payload (Should return 400 Bad Request)
    print("\n--- Testing 4: Edge Case - Empty Payload (POST /api/advice) ---")
    s4_payload = {}
    p4, _ = run_scenario("Scenario 4: Empty Payload Validation", s4_payload, expected_status=400)
    results.append(("Scenario 4: Empty Payload Validation (400)", p4))

    # Scenario 5: Partial Payload (Missing crop/soil/weather)
    print("\n--- Testing 5: Edge Case - Partial Data (POST /api/advice) ---")
    s5_payload = {"name": "Anil Sharma", "state": "Rajasthan"}
    p5, _ = run_scenario("Scenario 5: Partial Data Resilience", s5_payload, expected_status=200)
    results.append(("Scenario 5: Partial Data Resilience", p5))

    # Summary
    print("\n" + "#"*70)
    print("TEST SUITE SUMMARY")
    print("#"*70)
    all_passed = True
    for title, status in results:
        sym = "[PASS]" if status else "[FAIL]"
        print(f"- {title:45}: {sym}")
        if not status:
            all_passed = False
            
    print("\nOverall Status:", "ALL TESTS PASSED [SUCCESS]" if all_passed else "SOME TESTS FAILED [WARNING]")
    return all_passed

if __name__ == "__main__":
    run_all_tests()
