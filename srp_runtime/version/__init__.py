"""Milestone 2 version-domain types for SRP runtime."""

from .version_node import SemanticVersionNode
from .version_graph import SemanticVersionGraph
from .conflict import VersionConflict
from .conflict_detector import ConflictDetector
from .conflict_archive_adapter import ConflictArchiveEvidenceAdapter, ConflictEvidenceBundle
from .conflict_query import ConflictQuery, ConflictQueryResult, ConflictQueryService
from .resolution import ResolutionContext, ResolutionDecision, ResolutionDecisionService
