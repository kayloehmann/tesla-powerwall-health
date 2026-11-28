#!/usr/bin/env python3
"""Run the HACS integration gates against the local Gitea checkout."""

from __future__ import annotations

import json
import os
from pathlib import Path
import urllib.parse
import urllib.request

from custom_components.hacs.utils.validate import (
    HACS_MANIFEST_JSON_SCHEMA,
    INTEGRATION_MANIFEST_CATEGORIES_SCHEMA,
    INTEGRATION_MANIFEST_JSON_SCHEMA,
)
from voluptuous import Invalid
from voluptuous.humanize import humanize_error


ROOT = Path.cwd()
GITEA_API_URL = os.environ.get(
    "GITEA_API_URL", "https://gitea.loehmann.synology.me/api/v1"
).rstrip("/")
REPOSITORY = os.environ.get("CI_REPO", "kay/tesla-powerwall-health")
BRANDS_URL = "https://brands.home-assistant.io/domains.json"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def get_json(url: str) -> dict:
    request = urllib.request.Request(
        url,
        headers={"Accept": "application/json", "User-Agent": "hacs-gitea-validator/1"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def validate_schema(name: str, data: dict, schema) -> None:
    try:
        schema(data)
    except Invalid as error:
        raise RuntimeError(f"{name}: {humanize_error(data, error)}") from error


def validate_repository_metadata() -> None:
    owner, name = (urllib.parse.quote(part, safe="") for part in REPOSITORY.split("/", 1))
    metadata = get_json(f"{GITEA_API_URL}/repos/{owner}/{name}")
    checks = {
        "repository is archived": not metadata.get("archived", False),
        "repository has no description": bool(metadata.get("description")),
        "repository issues are disabled": bool(metadata.get("has_issues")),
        "repository has no topics": bool(metadata.get("topics")),
    }
    failures = [message for message, passed in checks.items() if not passed]
    if failures:
        raise RuntimeError("; ".join(failures))


def validate_license() -> None:
    candidates = [path for path in ROOT.iterdir() if path.name.lower().startswith("license")]
    if not candidates:
        raise RuntimeError("repository has no license file")
    # This repository uses MIT. Keep the check explicit instead of silently
    # accepting an arbitrary file named LICENSE.
    if "MIT License" not in candidates[0].read_text(encoding="utf-8"):
        raise RuntimeError("LICENSE is not the expected OSI-approved MIT license")


def main() -> None:
    manifests = sorted((ROOT / "custom_components").glob("*/manifest.json"))
    if len(manifests) != 1:
        raise RuntimeError(f"expected one integration manifest, found {len(manifests)}")

    manifest_path = manifests[0]
    manifest = load_json(manifest_path)
    hacs_manifest = load_json(ROOT / "hacs.json")
    if manifest.get("domain") != manifest_path.parent.name:
        raise RuntimeError("integration domain does not match its directory name")

    validate_schema("hacs.json", hacs_manifest, HACS_MANIFEST_JSON_SCHEMA)
    validate_schema("manifest.json", manifest, INTEGRATION_MANIFEST_JSON_SCHEMA)
    if "categories" in manifest:
        validate_schema(
            "manifest categories", manifest, INTEGRATION_MANIFEST_CATEGORIES_SCHEMA
        )

    if not any((ROOT / name).is_file() for name in ("README", "README.md", "INFO", "INFO.md")):
        raise RuntimeError("repository has no README or information file")
    validate_license()
    validate_repository_metadata()

    local_brand = manifest_path.parent / "brand" / "icon.png"
    if not local_brand.is_file():
        brands = get_json(BRANDS_URL)
        if manifest["domain"] not in brands.get("custom", {}):
            raise RuntimeError(
                "integration has neither a local brand icon nor a Home Assistant brand entry"
            )

    print("HACS local integration validation passed")


if __name__ == "__main__":
    main()
