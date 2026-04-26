import json
from pathlib import Path
from deepdiff import DeepDiff

def detect_schema_drift(manifest):
    snapshot_path = "target/last_manifest.json"

    # First time running — no previous snapshot exists
    if not Path(snapshot_path).exists():
        with open(snapshot_path, "w") as f:
            json.dump(manifest, f, indent=2)
        print("📁 No previous snapshot found. Saving current manifest as baseline.")
        return []

    # Load the previous manifest
    with open(snapshot_path, "r") as f:
        last_manifest = json.load(f)

    drifts = []

    for node_id, node in manifest["nodes"].items():
        if node["resource_type"] != "model":
            continue

        old_columns = last_manifest["nodes"].get(node_id, {}).get("columns", {})
        new_columns = node.get("columns", {})

        diff = DeepDiff(old_columns, new_columns, ignore_order=True)

        if diff:
            drifts.append({
                "model": node["name"],
                "changes": diff.to_dict()
            })
            print(f"⚠️  Schema drift detected in model: {node['name']}")
            for change_type, change_detail in diff.to_dict().items():
                print(f"   → {change_type}: {change_detail}")
        else:
            print(f"✅ No schema drift in model: {node['name']}")

    # Save current manifest as new snapshot
    with open(snapshot_path, "w") as f:
        json.dump(manifest, f, indent=2)

    return drifts


if __name__ == "__main__":
    # Test it standalone
    with open("target/manifest.json", "r") as f:
        manifest = json.load(f)

    drifts = detect_schema_drift(manifest)

    if not drifts:
        print("\n✅ No schema drift detected!")
    else:
        print(f"\n⚠️  Total drifts found: {len(drifts)}")