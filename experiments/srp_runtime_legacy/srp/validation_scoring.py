from typing import Iterable, List

from .validation_targets import SemanticContractGraph


def flatten_contract_phrases(validation_targets: Iterable | SemanticContractGraph) -> List[str]:
    if isinstance(validation_targets, SemanticContractGraph):
        return validation_targets.flattened_variants()
    flattened: List[str] = []
    for item in validation_targets:
        if isinstance(item, str):
            cleaned = item.strip()
            if cleaned:
                flattened.append(cleaned)
            continue
        try:
            values = [str(value).strip() for value in item if str(value).strip()]
        except TypeError:
            cleaned = str(item).strip()
            if cleaned:
                flattened.append(cleaned)
            continue
        flattened.extend(values)
    return flattened
