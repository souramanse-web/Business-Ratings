import argparse
import json
import sys
from urllib import request


def fetch_business_count(base_url: str) -> int:
    url = f"{base_url.rstrip('/')}/api/businesses"
    with request.urlopen(url, timeout=30) as response:
        payload = response.read().decode('utf-8')
        businesses = json.loads(payload)
        if not isinstance(businesses, list):
            raise ValueError(f"Unexpected response format from {url}")
        return len(businesses)


def main() -> int:
    parser = argparse.ArgumentParser(
        description='Weekly check: compare local and remote business counts.'
    )
    parser.add_argument('--local-url', default='http://127.0.0.1:5000', help='Local app base URL')
    parser.add_argument('--remote-url', required=True, help='Remote app base URL')
    parser.add_argument('--tolerated-diff', type=int, default=0, help='Allowed absolute difference before warning')
    args = parser.parse_args()

    try:
        local_count = fetch_business_count(args.local_url)
        remote_count = fetch_business_count(args.remote_url)
    except Exception as exc:
        print(f"CHECK_STATUS=ERROR; MESSAGE={exc}")
        return 2

    difference = abs(local_count - remote_count)
    print(f"LOCAL_BUSINESSES={local_count}")
    print(f"REMOTE_BUSINESSES={remote_count}")
    print(f"DIFFERENCE={difference}")

    if difference > args.tolerated_diff:
        print('CHECK_STATUS=WARNING')
        return 1

    print('CHECK_STATUS=OK')
    return 0


if __name__ == '__main__':
    sys.exit(main())
