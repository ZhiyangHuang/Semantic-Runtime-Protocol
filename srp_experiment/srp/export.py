import csv
from pathlib import Path
from typing import Dict, Iterable, List, Sequence


def _flatten_dict(prefix: str, value, output: Dict[str, object]) -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            nested_prefix = f"{prefix}_{key}" if prefix else key
            _flatten_dict(nested_prefix, item, output)
    else:
        output[prefix] = value


def flatten_record_for_csv(record: Dict[str, object]) -> Dict[str, object]:
    flat: Dict[str, object] = {}
    for key, value in record.items():
        if key == "lifecycle_summary" and isinstance(value, dict):
            _flatten_dict("lifecycle_summary", value, flat)
            continue
        if isinstance(value, dict):
            _flatten_dict(key, value, flat)
        else:
            flat[key] = value
    return flat


def flatten_records_for_csv(records: Sequence[Dict[str, object]]) -> List[Dict[str, object]]:
    return [flatten_record_for_csv(record) for record in records]


def _stringify_cell(value) -> str:
    if isinstance(value, list):
        return "|".join("" if item is None else str(item) for item in value)
    if isinstance(value, dict):
        return str(value)
    if value is None:
        return ""
    return str(value)


def write_records_csv(records: Sequence[Dict[str, object]], path: str | Path) -> Path:
    flattened = flatten_records_for_csv(records)
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames: List[str] = []
    for record in flattened:
        for key in record.keys():
            if key not in fieldnames:
                fieldnames.append(key)
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for record in flattened:
            writer.writerow({key: _stringify_cell(record.get(key)) for key in fieldnames})
    return output_path
