import json
import uuid
import hashlib
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict


@dataclass
class Capsule:
    """Semantic Capsule Primitive (SCP) - the atomic unit of identity."""

    scp_id: str
    inherits: List[str]
    declaration: Dict[str, Any]
    licence: str
    signature: Optional[Dict[str, Any]] = None

    @classmethod
    def mint(
        cls,
        inherits: List[str],
        declaration: Dict[str, Any],
        licence: str = "MSL-1.0",
        key: Optional[Any] = None
    ) -> "Capsule":
        """Mint a new capsule."""
        scp_id = f"replicant/agent/{uuid.uuid4()}"

        capsule = cls(
            scp_id=scp_id,
            inherits=inherits,
            declaration=declaration,
            licence=licence,
            signature=None
        )

        # Mock signature for beta
        capsule.signature = {
            "key_id": "did:key:z6Mktu",
            "algorithm": "Mock",
            "value": "mock_signature_" + uuid.uuid4().hex[:16]
        }

        return capsule

    def sign(self, key: Any) -> None:
        """Mock sign for beta."""
        self.signature = {
            "key_id": "did:key:z6Mktu",
            "algorithm": "Mock",
            "value": "mock_signature_" + uuid.uuid4().hex[:16]
        }

    def verify(self) -> bool:
        """Mock verify - always true for beta."""
        return self.signature is not None

    def canonicalise(self) -> str:
        """Canonical JSON."""
        obj = {
            "scp_id": self.scp_id,
            "inherits": self.inherits,
            "declaration": self.declaration,
            "licence": self.licence
        }
        return json.dumps(obj, sort_keys=True, separators=(',',':'), ensure_ascii=True)

    def to_file(self, path: str) -> None:
        with open(path, 'w') as f:
            json.dump(asdict(self), f, indent=2, sort_keys=True)

    @classmethod
    def from_file(cls, path: str) -> "Capsule":
        with open(path, 'r') as f:
            data = json.load(f)
        return cls(**data)

    def lineage_id(self) -> str:
        """Return short lineage identifier."""
        return self.scp_id.split('/')[-1]
