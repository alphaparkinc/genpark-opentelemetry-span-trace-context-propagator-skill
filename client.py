"""
W3C TraceContext and OpenTelemetry Span Tree Propagator.
Zero external dependencies, standard library only.
"""

import time
import uuid
import secrets
from typing import Dict, List, Any, Optional

class TraceContextPropagatorClient:
    """
    Implements W3C TraceContext specification (traceparent: 00-{trace_id}-{parent_id}-{trace_flags})
    and manages distributed hierarchical agent span execution trees.
    """

    def __init__(self):
        self.active_spans = {}
        self.completed_spans = []

    def generate_trace_id(self) -> str:
        """Generates 32-hex-character W3C trace ID."""
        return secrets.token_hex(16)

    def generate_span_id(self) -> str:
        """Generates 16-hex-character W3C span ID."""
        return secrets.token_hex(8)

    def format_traceparent(self, trace_id: str, span_id: str, sampled: bool = True) -> str:
        """Formats W3C traceparent header: 00-{trace_id}-{span_id}-{flags}"""
        flags = "01" if sampled else "00"
        return f"00-{trace_id}-{span_id}-{flags}"

    def parse_traceparent(self, header_value: str) -> Optional[Dict[str, Any]]:
        """Parses W3C traceparent header string."""
        parts = header_value.strip().split("-")
        if len(parts) != 4 or parts[0] != "00":
            return None
        return {
            "version": parts[0],
            "trace_id": parts[1],
            "parent_span_id": parts[2],
            "trace_flags": parts[3],
            "is_sampled": parts[3] == "01"
        }

    def start_span(self, name: str, trace_id: Optional[str] = None, parent_span_id: Optional[str] = None, attributes: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Starts a new agent span in the distributed trace tree."""
        t_id = trace_id or self.generate_trace_id()
        s_id = self.generate_span_id()
        start_ns = time.time_ns()

        span = {
            "name": name,
            "trace_id": t_id,
            "span_id": s_id,
            "parent_span_id": parent_span_id,
            "start_time_ns": start_ns,
            "end_time_ns": None,
            "duration_ms": None,
            "status": "UNSET",
            "attributes": attributes or {},
            "events": []
        }
        self.active_spans[s_id] = span
        return span

    def add_span_event(self, span_id: str, event_name: str, attributes: Optional[Dict[str, Any]] = None):
        """Records an event within an active span."""
        if span_id in self.active_spans:
            self.active_spans[span_id]["events"].append({
                "name": event_name,
                "timestamp_ns": time.time_ns(),
                "attributes": attributes or {}
            })

    def end_span(self, span_id: str, status: str = "OK") -> Optional[Dict[str, Any]]:
        """Ends an active span and calculates duration."""
        if span_id not in self.active_spans:
            return None
        span = self.active_spans.pop(span_id)
        span["end_time_ns"] = time.time_ns()
        span["duration_ms"] = round((span["end_time_ns"] - span["start_time_ns"]) / 1_000_000, 3)
        span["status"] = status
        self.completed_spans.append(span)
        return span

    def get_trace_tree(self, trace_id: str) -> List[Dict[str, Any]]:
        """Constructs hierarchical call tree for a given trace_id."""
        matching = [s for s in self.completed_spans if s["trace_id"] == trace_id]
        
        # Build hierarchy
        lookup = {s["span_id"]: dict(s, children=[]) for s in matching}
        root_spans = []

        for s in matching:
            s_id = s["span_id"]
            p_id = s["parent_span_id"]
            if p_id and p_id in lookup:
                lookup[p_id]["children"].append(lookup[s_id])
            else:
                root_spans.append(lookup[s_id])

        return root_spans
