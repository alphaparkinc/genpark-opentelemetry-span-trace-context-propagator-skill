"""
MCP Server for genpark-opentelemetry-span-trace-context-propagator-skill
Standard JSON-RPC 2.0 protocol over stdio.
"""

import sys
import json
from client import TraceContextPropagatorClient

client = TraceContextPropagatorClient()

def handle_request(req):
    req_id = req.get("id")
    method = req.get("method")
    params = req.get("params", {})

    if method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "tools": [
                    {
                        "name": "start_span",
                        "description": "Start an OpenTelemetry distributed trace span.",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "trace_id": {"type": "string"},
                                "parent_span_id": {"type": "string"},
                                "attributes": {"type": "object"}
                            },
                            "required": ["name"]
                        }
                    },
                    {
                        "name": "end_span",
                        "description": "End an OpenTelemetry span and record duration.",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "span_id": {"type": "string"},
                                "status": {"type": "string"}
                            },
                            "required": ["span_id"]
                        }
                    }
                ]
            }
        }
    elif method == "tools/call":
        tool_name = params.get("name")
        args = params.get("arguments", {})
        if tool_name == "start_span":
            res = client.start_span(args.get("name", ""), args.get("trace_id"), args.get("parent_span_id"), args.get("attributes"))
            return {"jsonrpc": "2.0", "id": req_id, "result": {"content": [{"type": "text", "text": json.dumps(res, indent=2)}]}}
        elif tool_name == "end_span":
            res = client.end_span(args.get("span_id", ""), args.get("status", "OK"))
            return {"jsonrpc": "2.0", "id": req_id, "result": {"content": [{"type": "text", "text": json.dumps(res, indent=2)}]}}
    return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": "Method not found"}}

def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
            resp = handle_request(req)
            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()
        except Exception as e:
            err = {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": str(e)}}
            sys.stdout.write(json.dumps(err) + "\n")
            sys.stdout.flush()

if __name__ == "__main__":
    main()
