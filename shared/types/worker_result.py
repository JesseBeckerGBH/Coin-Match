"""Shared WorkerResult type for all research workers."""
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

@dataclass
class WorkerResult:
    worker_name: str
    status: str  # "success", "error", "not_implemented"
    input_ref: Optional[str] = None
    output_ref: Optional[str] = None
    payload: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "worker_name": self.worker_name, "status": self.status,
            "input_ref": self.input_ref, "output_ref": self.output_ref,
            "payload": self.payload, "errors": self.errors, "metrics": self.metrics,
        }

    @property
    def is_success(self) -> bool:
        return self.status == "success"
