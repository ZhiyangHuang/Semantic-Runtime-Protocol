"""Operator-layer types for SRP runtime."""

from .base import SemanticOperator
from .approximation import ApproximationOperator
from .identity import IdentityUpdateOperator
from .activation import ActivationUpdateOperator
from .merge import MergeOperator
from .split import SplitOperator
from .recovery import RecoveryOperator
from .forgetting import ForgettingOperator
from .garbage_collection import GarbageCollectionOperator
from .relation import RelationUpdateOperator
