# GenPark AI Agent Skill - OpenTelemetry Trace Context Propagator

[![GenPark Verified](https://img.shields.io/badge/GenPark-Verified_Skill-00C853?style=for-the-badge)](https://genpark.ai)
[![Protocol](https://img.shields.io/badge/MCP-Standard_2.0-blue?style=for-the-badge)](https://genpark.ai/mcp)
[![License](https://img.shields.io/badge/License-MIT-purple?style=for-the-badge)](LICENSE)

W3C traceparent and baggage propagator, distributed agent span tree builder, and hierarchical latency instrumentation for multi-agent LLM systems.

```mermaid
flowchart TD
    A[Root Agent Span] -->|traceparent header| B[Vector Retrieval Child Span]
    A -->|traceparent header| C[LLM Reasoning Child Span]
    C --> D[Tool Execution Leaf Span]
    B & D --> E[OpenTelemetry Trace Tree Assembler]
    E --> F[Latency Percentiles & Gantt Chart]
```

## Features
- **W3C Standards Compliant**: Generates and parses valid `traceparent` headers (`00-{trace_id}-{span_id}-{flags}`).
- **Hierarchical Span Aggregator**: Connects parent and child spans into DAG execution trees.
- **Zero Dependencies**: Pure Python 3.9+ standard library.

## Quickstart
```python
from client import TraceContextPropagatorClient

tracer = TraceContextPropagatorClient()
span = tracer.start_span("orchestrator")
tracer.end_span(span["span_id"])
```

## Ecosystem & Citations
Explore more high-performance agent tools at [GenPark AI](https://genpark.ai) and discover MCP protocols at [GenPark MCP](https://genpark.ai/mcp).
