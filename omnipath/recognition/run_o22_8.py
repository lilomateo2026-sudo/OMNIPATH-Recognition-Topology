import json
from pathlib import Path
from promotion_registry_audit import audit_registry

HERE = Path(__file__).resolve().parent
REGISTRY = HERE / "promotion_registry" / "registry.json"


def main():
    data = json.loads(REGISTRY.read_text(encoding="utf-8"))
    result = audit_registry(data)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["valid"] else 8


if __name__ == "__main__":
    raise SystemExit(main())
