import argparse
import json
import sys
from urllib import error, parse, request
from http.cookiejar import CookieJar

from app import app, Business


def _json_request(opener, method, url, payload=None):
    data = None
    headers = {"Accept": "application/json"}

    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"

    req = request.Request(url, data=data, headers=headers, method=method)
    with opener.open(req, timeout=30) as response:
        body = response.read().decode("utf-8")
        return response.getcode(), json.loads(body) if body else None


def fetch_local_businesses():
    with app.app_context():
        businesses = Business.query.all()
        return [
            {
                "name": b.name,
                "description": b.description or "",
                "location": b.location or "",
                "website": b.website or "",
                "sector": b.sector.name if b.sector else None,
            }
            for b in businesses
            if b.name
        ]


def build_opener():
    cookie_jar = CookieJar()
    return request.build_opener(request.HTTPCookieProcessor(cookie_jar))


def main():
    parser = argparse.ArgumentParser(
        description="Sync missing local businesses to a remote Business Ratings instance."
    )
    parser.add_argument("--remote-url", required=True, help="Remote base URL, e.g. https://business-rating-app.onrender.com")
    parser.add_argument("--username", required=True, help="Admin username on remote")
    parser.add_argument("--password", required=True, help="Admin password on remote")
    parser.add_argument("--dry-run", action="store_true", help="Only print missing businesses without creating them")
    args = parser.parse_args()

    remote_url = args.remote_url.rstrip("/")
    opener = build_opener()

    try:
        status, login_response = _json_request(
            opener,
            "POST",
            f"{remote_url}/login",
            {"username": args.username, "password": args.password},
        )
    except error.HTTPError as exc:
        message = exc.read().decode("utf-8", errors="ignore")
        print(f"Login failed ({exc.code}): {message}")
        return 1
    except Exception as exc:
        print(f"Login error: {exc}")
        return 1

    if status != 200:
        print(f"Login failed with status {status}: {login_response}")
        return 1

    try:
        _, remote_sectors = _json_request(opener, "GET", f"{remote_url}/admin/sectors")
        _, remote_businesses = _json_request(opener, "GET", f"{remote_url}/admin/businesses")
    except error.HTTPError as exc:
        message = exc.read().decode("utf-8", errors="ignore")
        print(f"Failed to fetch remote admin data ({exc.code}): {message}")
        return 1
    except Exception as exc:
        print(f"Failed to fetch remote data: {exc}")
        return 1

    local_businesses = fetch_local_businesses()
    remote_names = {b.get("name") for b in (remote_businesses or []) if b.get("name")}
    sector_map = {s.get("name"): s.get("id") for s in (remote_sectors or []) if s.get("name") and s.get("id")}

    missing = [b for b in local_businesses if b["name"] not in remote_names]

    print(f"Local businesses: {len(local_businesses)}")
    print(f"Remote businesses: {len(remote_businesses or [])}")
    print(f"Missing on remote: {len(missing)}")

    if not missing:
        print("Remote already has all local businesses.")
        return 0

    missing_sector_names = sorted({b["sector"] for b in missing if b.get("sector") and b["sector"] not in sector_map})
    if missing_sector_names:
        print("Cannot sync because these sectors are missing on remote:")
        for name in missing_sector_names:
            print(f"- {name}")
        print("Create those sectors first in /admin, then rerun.")
        return 1

    if args.dry_run:
        print("Dry run complete. Businesses that would be created:")
        for business in missing:
            print(f"- {business['name']} ({business.get('sector') or 'No sector'})")
        return 0

    created = 0
    for business in missing:
        payload = {
            "name": business["name"],
            "description": business.get("description", ""),
            "location": business.get("location", ""),
            "website": business.get("website", ""),
            "sector_id": sector_map.get(business.get("sector")),
        }

        try:
            status, _ = _json_request(opener, "POST", f"{remote_url}/admin/businesses", payload)
            if status in (200, 201):
                created += 1
                print(f"Created: {business['name']}")
            else:
                print(f"Skipped {business['name']} (status {status})")
        except error.HTTPError as exc:
            message = exc.read().decode("utf-8", errors="ignore")
            print(f"Failed {business['name']} ({exc.code}): {message}")
        except Exception as exc:
            print(f"Failed {business['name']}: {exc}")

    print(f"Sync complete. Created {created} business(es).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
