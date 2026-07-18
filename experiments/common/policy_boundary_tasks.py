from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass(frozen=True)
class PolicyBoundaryTask:
    name: str
    task: Dict[str, Any]
    semantic_unit_count: int


def _dependency_object(dependency_id: str, subject_value: str, relation_value: str, object_value: str) -> Dict[str, Any]:
    return {
        "dependency_id": dependency_id,
        "subject": {
            "type": "entity",
            "canonical": subject_value,
        },
        "relation": {
            "type": "relation",
            "canonical": relation_value,
        },
        "object": {
            "type": "entity",
            "canonical": object_value,
        },
    }


def _validation_dependency_object(dependency_id: str, surface: str) -> Dict[str, Any]:
    return {
        "dependency_id": dependency_id,
        "concept": "fact",
        "normalized_value": surface,
        "surface": surface,
    }


def _pressure_task() -> PolicyBoundaryTask:
    critical_clauses = [
        ("Aster", "keeps", "reactor alpha stable"),
        ("Boreal", "keeps", "coolant beta stable"),
        ("Cinder", "keeps", "sensor gamma aligned"),
        ("Dune", "keeps", "access delta sealed"),
        ("Ember", "keeps", "power epsilon routed"),
        ("Fjord", "keeps", "backup zeta primed"),
    ]
    decoy_clauses = [
        ("Gale", "keeps", "alarms eta routed"),
        ("Harbor", "keeps", "logbook theta sealed"),
        ("Ion", "keeps", "tokens iota rotated"),
        ("Jade", "keeps", "maintenance kappa closed"),
        ("Kite", "keeps", "shuttle lambda scheduled"),
        ("Lumen", "keeps", "gate mu sealed"),
        ("Mosaic", "keeps", "reports nu archived"),
        ("Nexus", "keeps", "override xi blocked"),
        ("Orbit", "keeps", "telemetry omicron stable"),
        ("Pulse", "keeps", "fallback pi ready"),
        ("Quill", "keeps", "auxiliary rails rho aligned"),
        ("Ridge", "keeps", "secondary valves sigma closed"),
        ("Sol", "keeps", "sideband tau quiet"),
        ("Tundra", "keeps", "buffer upsilon primed"),
        ("Umber", "keeps", "shadow links phi dormant"),
        ("Vega", "keeps", "spare relays chi ready"),
        ("Wisp", "keeps", "satellite nodes psi parked"),
        ("Xeno", "keeps", "fallback channels omega sealed"),
        ("Yarrow", "keeps", "auxiliary mesh eta calm"),
        ("Zephyr", "keeps", "backup trace lambda silent"),
    ]
    clauses = critical_clauses + decoy_clauses
    memory = ". ".join(f"{subject} {relation} {obj}" for subject, relation, obj in clauses) + "."
    constraints = [f"{subject} {relation} {obj}." for subject, relation, obj in critical_clauses]
    dependency_objects = [
        _dependency_object(f"dep-{index}", subject, relation, obj)
        for index, (subject, relation, obj) in enumerate(clauses, start=1)
    ]
    expected_keywords = [
        "aster",
        "boreal",
        "cinder",
        "dune",
        "ember",
        "fjord",
        "gale",
        "harbor",
        "ion",
        "jade",
        "kite",
        "lumen",
        "mosaic",
        "nexus",
        "orbit",
        "pulse",
        "quill",
        "ridge",
        "sol",
        "tundra",
        "umber",
        "vega",
        "wisp",
        "xeno",
        "yarrow",
        "zephyr",
        "reactor",
        "coolant",
        "sensor",
        "access",
        "power",
        "backup",
        "alarms",
        "logbook",
        "tokens",
        "maintenance",
        "shuttle",
        "gate",
        "reports",
        "override",
        "telemetry",
        "fallback",
    ]
    important_objects = [
        {
            "object_id": f"boundary:{index}",
            "type": "constraint",
            "value": f"{subject} {relation} {obj}.",
            "confidence": 1.0,
            "evidence_pointer": f"memory:{index}",
        }
        for index, (subject, relation, obj) in enumerate(clauses, start=1)
    ]
    task = {
        "id": "policy-boundary-memory-saturation",
        "task_type": "policy_boundary_analysis",
        "source": "SRP Policy Boundary Analysis",
        "initial_state": {
            "constraints": constraints,
            "memory": memory,
        },
        "queries": [
            "Preserve the full reactor map and keep the module assignments stable.",
        ],
        "query_expectations": [[[constraint] for constraint in constraints]],
        "expected_keywords": expected_keywords,
        "semantic_dependencies": {
            "required_dependency_objects": dependency_objects,
        },
        "metadata": {
            "benchmark": "SRP Policy Boundary Analysis",
            "scenario": "memory_saturation",
            "pressure_mode": "memory_saturation",
            "semantic_unit_count": len(constraints) + len(clauses) + len(expected_keywords),
            "required_dependency_labels": constraints,
            "required_dependency_objects": dependency_objects,
            "important_objects": important_objects,
        },
    }
    return PolicyBoundaryTask(
        name="memory_saturation",
        task=task,
        semantic_unit_count=int(task["metadata"]["semantic_unit_count"]),
    )


def _validation_pressure_task() -> PolicyBoundaryTask:
    bridge_facts = [
        "Bridge alpha keeps the blue key aligned with the archive gate.",
        "Archive gate stays open only after bridge alpha is confirmed.",
        "Bridge beta keeps the red key aligned with the transit rail.",
        "Transit rail stays open only after bridge beta is confirmed.",
        "Bridge gamma keeps the green key aligned with the relay shelf.",
        "Relay shelf stays open only after bridge gamma is confirmed.",
        "Bridge delta keeps the orange key aligned with the access lock.",
        "Access lock stays open only after bridge delta is confirmed.",
    ]
    decoy_facts = [
        "Harbor keeps the logbook quiet.",
        "Ion keeps the telemetry stable.",
        "Jade keeps the maintenance buffer closed.",
        "Kite keeps the shuttle schedule clean.",
        "Lumen keeps the fallback lane silent.",
        "Mosaic keeps the report stack archived.",
        "Nexus keeps the override channel blocked.",
        "Orbit keeps the telemetry channel aligned.",
        "Pulse keeps the backup mirror ready.",
        "Quill keeps the sidecar notes concise.",
        "Ridge keeps the auxiliary valves closed.",
        "Sol keeps the sideband quiet.",
        "Tundra keeps the buffer primed.",
        "Umber keeps the shadow links dormant.",
        "Vega keeps the spare relays ready.",
        "Wisp keeps the satellite nodes parked.",
        "Xeno keeps the trace channels sealed.",
        "Yarrow keeps the auxiliary mesh calm.",
        "Zephyr keeps the backup trace silent.",
        "Atlas keeps the calibration deck clean.",
    ]
    clauses = bridge_facts + decoy_facts
    memory = ". ".join(clauses) + "."
    constraints = [
        "Bridge alpha keeps the blue key aligned with the archive gate.",
        "Bridge beta keeps the red key aligned with the transit rail.",
    ]
    dependency_objects = [
        _validation_dependency_object(f"dep-{index}", surface)
        for index, surface in enumerate(bridge_facts, start=1)
    ]
    expected_keywords = [
        "bridge",
        "alpha",
        "beta",
        "gamma",
        "delta",
        "blue",
        "red",
        "green",
        "orange",
        "archive",
        "transit",
        "relay",
        "lock",
        "confirmed",
    ]
    important_objects = [
        {
            "object_id": "bridge-alpha",
            "type": "fact",
            "value": bridge_facts[0],
            "confidence": 1.0,
            "evidence_pointer": "memory:1",
        },
        {
            "object_id": "bridge-beta",
            "type": "fact",
            "value": bridge_facts[2],
            "confidence": 1.0,
            "evidence_pointer": "memory:3",
        },
    ]
    task = {
        "id": "policy-boundary-validation-pressure",
        "task_type": "policy_boundary_analysis",
        "source": "SRP Policy Boundary Analysis",
        "initial_state": {
            "constraints": constraints,
            "memory": memory,
        },
        "queries": [
            "Preserve the bridge dependencies that keep the archive, transit, relay, and access paths valid.",
        ],
        "query_expectations": [[[fact] for fact in bridge_facts]],
        "expected_keywords": expected_keywords,
        "semantic_dependencies": {
            "required_dependency_objects": dependency_objects,
        },
        "metadata": {
            "benchmark": "SRP Policy Boundary Analysis",
            "scenario": "validation_pressure",
            "pressure_mode": "validation_pressure",
            "semantic_unit_count": len(constraints) + len(clauses) + len(expected_keywords),
            "required_dependency_labels": bridge_facts,
            "required_dependency_objects": dependency_objects,
            "important_objects": important_objects,
        },
    }
    return PolicyBoundaryTask(
        name="validation_pressure",
        task=task,
        semantic_unit_count=int(task["metadata"]["semantic_unit_count"]),
    )


def _dependency_f1_pressure_task() -> PolicyBoundaryTask:
    bridge_facts = [
        "Bridge alpha keeps the blue key aligned with the archive gate.",
        "Bridge beta keeps the red key aligned with the transit rail.",
        "Bridge gamma keeps the green key aligned with the relay shelf.",
        "Bridge delta keeps the orange key aligned with the access lock.",
        "Bridge epsilon keeps the silver key aligned with the signal vault.",
        "Bridge zeta keeps the amber key aligned with the vault latch.",
        "Bridge eta keeps the violet key aligned with the control hinge.",
        "Bridge theta keeps the white key aligned with the timing lock.",
    ]
    near_duplicate_decoys = [
        "Bridge alpha keeps the archive key aligned with the blue gate.",
        "Bridge beta keeps the transit key aligned with the red rail.",
        "Bridge gamma keeps the relay key aligned with the green shelf.",
        "Bridge delta keeps the access key aligned with the orange lock.",
        "Bridge epsilon keeps the signal key aligned with the silver vault.",
        "Bridge zeta keeps the vault key aligned with the amber latch.",
        "Bridge eta keeps the control key aligned with the violet hinge.",
        "Bridge theta keeps the timing key aligned with the white lock.",
    ]
    filler_facts = [
        "Harbor keeps the logbook quiet.",
        "Ion keeps the telemetry stable.",
        "Jade keeps the maintenance buffer closed.",
        "Kite keeps the shuttle schedule clean.",
        "Lumen keeps the fallback lane silent.",
        "Mosaic keeps the report stack archived.",
        "Nexus keeps the override channel blocked.",
        "Orbit keeps the telemetry channel aligned.",
        "Pulse keeps the backup mirror ready.",
        "Quill keeps the sidecar notes concise.",
        "Ridge keeps the auxiliary valves closed.",
        "Sol keeps the sideband quiet.",
        "Tundra keeps the buffer primed.",
        "Umber keeps the shadow links dormant.",
        "Vega keeps the spare relays ready.",
        "Wisp keeps the satellite nodes parked.",
        "Xeno keeps the trace channels sealed.",
        "Yarrow keeps the auxiliary mesh calm.",
        "Zephyr keeps the backup trace silent.",
        "Atlas keeps the calibration deck clean.",
    ]
    clauses = bridge_facts + near_duplicate_decoys + filler_facts
    memory = ". ".join(clauses) + "."
    constraints = bridge_facts[:4]
    dependency_objects = [
        _validation_dependency_object(f"dep-{index}", surface)
        for index, surface in enumerate(bridge_facts, start=1)
    ]
    expected_keywords = [
        "bridge",
        "alpha",
        "beta",
        "gamma",
        "delta",
        "epsilon",
        "zeta",
        "eta",
        "theta",
        "blue",
        "red",
        "green",
        "orange",
        "silver",
        "amber",
        "violet",
        "white",
        "archive",
        "transit",
        "relay",
        "access",
        "signal",
        "vault",
        "latch",
        "hinge",
        "timing",
        "lock",
        "confirmed",
    ]
    important_objects = [
        {
            "object_id": f"bridge-{name}",
            "type": "fact",
            "value": surface,
            "confidence": 1.0,
            "evidence_pointer": f"memory:{index}",
        }
        for index, (name, surface) in enumerate(zip(["alpha", "beta", "gamma", "delta", "epsilon", "zeta", "eta", "theta"], bridge_facts), start=1)
    ]
    task = {
        "id": "policy-boundary-dependency-f1",
        "task_type": "policy_boundary_analysis",
        "source": "SRP Policy Boundary Analysis",
        "initial_state": {
            "constraints": constraints,
            "memory": memory,
        },
        "queries": [
            "Preserve the bridge dependencies that keep the archive, transit, relay, and access paths valid.",
        ],
        "query_expectations": [[[fact] for fact in bridge_facts]],
        "expected_keywords": expected_keywords,
        "semantic_dependencies": {
            "required_dependency_objects": dependency_objects,
        },
        "metadata": {
            "benchmark": "SRP Policy Boundary Analysis",
            "scenario": "dependency_f1_pressure",
            "pressure_mode": "dependency_f1_pressure",
            "semantic_unit_count": len(constraints) + len(clauses) + len(expected_keywords),
            "required_dependency_labels": bridge_facts,
            "required_dependency_objects": dependency_objects,
            "important_objects": important_objects,
        },
    }
    return PolicyBoundaryTask(
        name="dependency_f1_pressure",
        task=task,
        semantic_unit_count=int(task["metadata"]["semantic_unit_count"]),
    )


def build_policy_boundary_tasks() -> List[PolicyBoundaryTask]:
    return [_pressure_task(), _validation_pressure_task(), _dependency_f1_pressure_task()]
