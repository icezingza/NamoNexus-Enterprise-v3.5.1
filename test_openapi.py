#!/usr/bin/env python3
"""Debug script to test /openapi.json endpoint."""

import json
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from main import app
    from fastapi.testclient import TestClient
    
    client = TestClient(app)
    
    print("Testing /health endpoint...")
    response = client.get("/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()
    
    print("Testing /openapi.json endpoint...")
    response = client.get("/openapi.json")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        openapi_spec = response.json()
        print("✓ OpenAPI spec retrieved successfully")
        print(f"  Title: {openapi_spec.get('info', {}).get('title', 'N/A')}")
        print(f"  Version: {openapi_spec.get('info', {}).get('version', 'N/A')}")
        print(f"  Routes: {len(openapi_spec.get('paths', {}))}")
        for path in sorted(openapi_spec.get('paths', {}).keys()):
            methods = list(openapi_spec['paths'][path].keys())
            print(f"    {path} [{', '.join(methods)}]")
    else:
        print(f"✗ Failed to get OpenAPI spec")
        print(f"  Response: {response.text[:500]}")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
