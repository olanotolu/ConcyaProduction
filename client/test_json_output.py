#!/usr/bin/env python3
"""
Quick test script to validate JSON output format.
"""

import json
import sys


def test_json_format():
    """Test that our JSON output format is valid."""
    # Expected format
    expected_fields = {"timestamp", "text", "speaker", "confidence"}
    
    # Sample outputs
    samples = [
        '{"timestamp": 1730940001.25, "text": "hello can you hear me", "speaker": "user", "confidence": 0.95}',
        '{"timestamp": 1730940005.12, "text": "awesome this is working", "speaker": "user", "confidence": 0.95}',
    ]
    
    print("Testing JSON output format...\n")
    
    for i, sample in enumerate(samples, 1):
        print(f"Test {i}: {sample}")
        
        try:
            data = json.loads(sample)
            
            # Check all required fields are present
            if not expected_fields.issubset(data.keys()):
                missing = expected_fields - data.keys()
                print(f"  ❌ FAIL: Missing fields: {missing}")
                return False
            
            # Validate field types
            if not isinstance(data['timestamp'], (int, float)):
                print(f"  ❌ FAIL: timestamp must be numeric")
                return False
            
            if not isinstance(data['text'], str):
                print(f"  ❌ FAIL: text must be string")
                return False
            
            if not isinstance(data['speaker'], str):
                print(f"  ❌ FAIL: speaker must be string")
                return False
            
            if not isinstance(data['confidence'], (int, float)):
                print(f"  ❌ FAIL: confidence must be numeric")
                return False
            
            if not (0.0 <= data['confidence'] <= 1.0):
                print(f"  ❌ FAIL: confidence must be between 0.0 and 1.0")
                return False
            
            print(f"  ✅ PASS: Valid JSON format")
            print(f"     - Timestamp: {data['timestamp']}")
            print(f"     - Text: '{data['text']}'")
            print(f"     - Speaker: {data['speaker']}")
            print(f"     - Confidence: {data['confidence']}")
            print()
            
        except json.JSONDecodeError as e:
            print(f"  ❌ FAIL: Invalid JSON: {e}")
            return False
    
    print("✅ All tests passed!")
    return True


if __name__ == "__main__":
    success = test_json_format()
    sys.exit(0 if success else 1)

