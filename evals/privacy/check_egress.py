#!/usr/bin/env python3
"""Privacy promise test: check captured network traffic from an automated test run.

Input: JSONL, one request per line, as exported from the test proxy:
  {"host": "api.example.com", "path": "/v1/x", "body": "..."}
Fails if a request goes to a host not in allowlist.txt, or if any request body,
path or query contains a canary string planted in the test library
(canaries.txt). Canaries are unique phrases inserted into test saves,
transcripts, notes and questions; seeing one on the wire means content left
the phone.

Usage: python3 check_egress.py CAPTURE.jsonl [--json]
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def load_list(name):
    with open(os.path.join(HERE, name), encoding="utf-8") as f:
        return [l.strip() for l in f if l.strip() and not l.startswith("#")]


def host_allowed(host, allow):
    host = host.lower()
    for a in allow:
        a = a.split()[0].lower()
        if a.startswith("*.") and (host.endswith(a[1:]) or host == a[2:]):
            return True
        if host == a:
            return True
    return False


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)
    allow = load_list("allowlist.txt")
    canaries = load_list("canaries.txt")
    problems = []
    with open(sys.argv[1], encoding="utf-8") as f:
        for n, line in enumerate(f, 1):
            if not line.strip():
                continue
            req = json.loads(line)
            host = req.get("host", "")
            if not host_allowed(host, allow):
                problems.append(f"line {n}: host not on allowlist: {host}")
            blob = " ".join(str(req.get(k, "")) for k in ("path", "query", "body"))
            for c in canaries:
                if c in blob:
                    problems.append(f"line {n}: user content (canary '{c}') sent to {host}")
    passed = not problems
    if "--json" in sys.argv:
        print(json.dumps({"suite": "privacy", "passed": passed, "problems": problems}))
    else:
        print("PASS: no user content left the device" if passed else "FAIL:\n" + "\n".join(problems))
    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
