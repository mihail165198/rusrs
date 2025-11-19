#!/usr/bin/env python3
"""
Script to fetch AWS IPv4 ranges and save them to a text file
"""

import requests
import json
from typing import List, Set

def fetch_aws_ip_ranges() -> List[str]:
    """Fetch AWS IP ranges from official source"""
    url = "https://ip-ranges.amazonaws.com/ip-ranges.json"
    
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        ip_ranges = set()
        
        # Extract IPv4 prefixes
        for prefix in data.get('prefixes', []):
            if 'ip_prefix' in prefix:
                ip_ranges.add(prefix['ip_prefix'])
        
        # Extract IPv6 prefixes (commented out since we only want IPv4)
        # for prefix in data.get('ipv6_prefixes', []):
        #     if 'ipv6_prefix' in prefix:
        #         ip_ranges.add(prefix['ipv6_prefix'])
        
        return sorted(list(ip_ranges))
        
    except requests.RequestException as e:
        print(f"Error fetching AWS IP ranges: {e}")
        return []
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON response: {e}")
        return []

def save_ip_ranges(ip_ranges: List[str], filename: str = "aws.txt") -> bool:
    """Save IP ranges to text file"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            for ip_range in ip_ranges:
                f.write(ip_range + '\n')
        
        print(f"Successfully saved {len(ip_ranges)} IP ranges to {filename}")
        return True
        
    except Exception as e:
        print(f"Error saving IP ranges: {e}")
        return False

def main():
    print("Fetching AWS IP ranges...")
    ip_ranges = fetch_aws_ip_ranges()
    
    if ip_ranges:
        print(f"Found {len(ip_ranges)} IPv4 ranges")
        if save_ip_ranges(ip_ranges):
            print("File created successfully: aws.txt")
        else:
            print("Failed to create file")
            exit(1)
    else:
        print("No IP ranges found")
        exit(1)

if __name__ == "__main__":
    main()