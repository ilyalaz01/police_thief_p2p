"""Single public entry point composed from cohesive stateless SDK services."""

from dataclasses import dataclass, field

from .artifacts import ArtifactsSDK
from .configuration import ConfigurationSDK
from .domain import DomainSDK
from .evaluation import EvaluationSDK
from .policies import PoliciesSDK
from .transport import TransportSDK


@dataclass(frozen=True, slots=True)
class PoliceThiefSDK:
    """Single consumer entry point for all project business operations."""

    domain: DomainSDK = field(default_factory=DomainSDK)
    policies: PoliciesSDK = field(default_factory=PoliciesSDK)
    evaluation: EvaluationSDK = field(default_factory=EvaluationSDK)
    artifacts: ArtifactsSDK = field(default_factory=ArtifactsSDK)
    transport: TransportSDK = field(default_factory=TransportSDK)
    configuration: ConfigurationSDK = field(default_factory=ConfigurationSDK)
