from __future__ import annotations

from dataclasses import dataclass, field

from .version_node import SemanticVersionNode


@dataclass
class SemanticVersionGraph:
    nodes: dict[str, SemanticVersionNode] = field(default_factory=dict)

    def add_version(self, node: SemanticVersionNode) -> None:
        self.nodes[node.version_id] = node

    def has_version(self, version_id: str) -> bool:
        return version_id in self.nodes

    def upsert_version(self, node: SemanticVersionNode) -> None:
        self.nodes[node.version_id] = node

    def get_version(self, version_id: str) -> SemanticVersionNode:
        return self.nodes[version_id]

    def get_parents(self, version_id: str) -> list[SemanticVersionNode]:
        node = self.nodes[version_id]
        return [self.nodes[parent_id] for parent_id in node.parent_versions if parent_id in self.nodes]

    def get_children(self, version_id: str) -> list[SemanticVersionNode]:
        return [node for node in self.nodes.values() if version_id in node.parent_versions]
