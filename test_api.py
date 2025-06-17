#!/usr/bin/env python3
"""
Test script for the Job Search Flask API.
"""
import requests
import json
import time

BASE_URL = "http://localhost:8080"


def _print_test_header(name):
  print("\n" + "=" * 30)
  print(f"  Testing: {name}")
  print("=" * 30)


def _print_response(response):
  print(f"Status Code: {response.status_code}")
  try:
    print(f"Response: {json.dumps(response.json(), indent=2)}")
  except json.JSONDecodeError:
    print(f"Response (non-JSON): {response.text}")


def test_health_endpoint():
  """Test the health check endpoint."""
  _print_test_header("Health Check")
  try:
    response = requests.get(f"{BASE_URL}/health")
    _print_response(response)
    return response.status_code in (200, 503)
  except requests.ConnectionError as e:
    print(f"Error: {e}")
    return False


def test_jobs_endpoint():
  """Test the /jobs search endpoint."""
  _print_test_header("Job Search")
  try:
    test_data = {
        "query": "Senior Software Engineer",
        "tech_skills": ["Python", "Flask", "MongoDB"],
        "job_level": "Senior"
    }

    response = requests.post(
        f"{BASE_URL}/jobs",
        headers={"Content-Type": "application/json"},
        data=json.dumps(test_data)
    )

    _print_response(response)
    return response.status_code == 200 and response.json().get('success') is True
  except requests.ConnectionError as e:
    print(f"Error: {e}")
    return False


def test_questions_endpoint():
  """Test the /questions generation endpoint."""
  _print_test_header("Question Generation")
  try:
    test_data = {
        "job": {
            "title": "Cloud Solutions Architect",
            "description": "Designing and deploying scalable cloud infrastructure.",
            "skills": [
                "AWS",
                "Kubernetes",
                "Terraform"]}}

    response = requests.post(
        f"{BASE_URL}/questions",
        headers={"Content-Type": "application/json"},
        data=json.dumps(test_data)
    )

    _print_response(response)
    return response.status_code == 200 and response.json().get('success') is True
  except requests.ConnectionError as e:
    print(f"Error: {e}")
    return False


def main():
  """Run all API tests."""
  print("=" * 50)
  print(" Job Search API Test Suite")
  print("=" * 50)

  print(f"Testing API at: {BASE_URL}")
  print("Please ensure the Flask application is running.")
  print("You can run it with: python main.py")

  try:
    input("\nPress Enter to start tests...")
  except KeyboardInterrupt:
    print("\nTests cancelled.")
    return

  tests = [
      ("Health Check", test_health_endpoint),
      ("Job Search", test_jobs_endpoint),
      ("Question Generation", test_questions_endpoint),
  ]

  results = []
  for test_name, test_func in tests:
    success = test_func()
    results.append((test_name, success))
    time.sleep(1)

  print("\n" + "=" * 50)
  print("  TEST RESULTS SUMMARY")
  print("=" * 50)

  for test_name, success in results:
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{test_name}: {status}")

  total_passed = sum(1 for _, success in results if success)
  print(f"\nPassed: {total_passed}/{len(results)} tests")
  print("=" * 50)


if __name__ == "__main__":
  main()
