"""
Demonstration of genpark-opentelemetry-span-trace-context-propagator-skill
"""

import time
from client import TraceContextPropagatorClient

def main():
    tracer = TraceContextPropagatorClient()

    # Root Agent Invocation
    root_span = tracer.start_span("agent_orchestration_root", attributes={"model": "claude-3-5-sonnet", "user": "usr_99"})
    trace_id = root_span["trace_id"]
    root_id = root_span["span_id"]
    
    traceparent_header = tracer.format_traceparent(trace_id, root_id)
    print("Injected HTTP traceparent:", traceparent_header)

    # Sub-task 1: Tool execution
    child1 = tracer.start_span("vector_db_retrieval", trace_id=trace_id, parent_span_id=root_id, attributes={"top_k": 5})
    time.sleep(0.02)
    tracer.add_span_event(child1["span_id"], "query_embedded", {"dims": 1536})
    tracer.end_span(child1["span_id"], status="OK")

    # Sub-task 2: LLM generation
    child2 = tracer.start_span("llm_reasoning_step", trace_id=trace_id, parent_span_id=root_id, attributes={"temperature": 0.2})
    time.sleep(0.03)
    tracer.end_span(child2["span_id"], status="OK")

    # Finish root
    tracer.end_span(root_id, status="OK")

    tree = tracer.get_trace_tree(trace_id)
    print("\n=== HIERARCHICAL DISTRIBUTED TRACE TREE ===")
    def print_node(node, indent=0):
        print(f"{'  ' * indent}- [{node['status']}] {node['name']} ({node['duration_ms']} ms) [Span: {node['span_id'][:8]}...]")
        for c in node.get("children", []):
            print_node(c, indent + 1)

    for r in tree:
        print_node(r)

if __name__ == "__main__":
    main()
