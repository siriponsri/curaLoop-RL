"""Pinned MCP2025-11-25 stdio subset. No model, network or destination client."""

import argparse
import json
import math
import sys
from pathlib import Path

from .portfolio_v1 import Portfolio, TOOLS, VERSION

MAX_MESSAGE_BYTES = 1024 * 1024
PROTOCOL = '2025-11-25'


def parse_message(raw):
    if type(raw) is not bytes or len(raw) > MAX_MESSAGE_BYTES:
        raise ValueError('Bounded message required')
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result: raise ValueError('Duplicate JSON key')
            result[key] = value
        return result
    def constant(value): raise ValueError('Nonfinite JSON denied')
    def number(value):
        parsed = float(value)
        if not math.isfinite(parsed): raise ValueError('Nonfinite JSON denied')
        return parsed
    return json.loads(raw.decode('utf-8'), object_pairs_hook=pairs, parse_constant=constant, parse_float=number)


class Session:
    def __init__(self, portfolio):
        self.portfolio, self.initialized, self.ready = portfolio, False, False

    @staticmethod
    def error(identity, code, message):
        return {'jsonrpc': '2.0', 'id': identity, 'error': {'code': code, 'message': message}}

    def handle(self, request):
        if type(request) is not dict or request.get('jsonrpc') != '2.0' or type(request.get('method')) is not str:
            return self.error(None, -32600, 'INVALID_REQUEST')
        identity = request.get('id')
        if 'id' in request and (type(identity) not in (str, int) or type(identity) is bool):
            return self.error(None, -32600, 'INVALID_REQUEST_ID')
        method, params = request['method'], request.get('params', {})
        if type(params) is not dict:
            return self.error(identity, -32602, 'INVALID_PARAMS') if 'id' in request else None
        params = dict(params)
        metadata = params.pop('_meta', {})
        if type(metadata) is not dict:
            return self.error(identity, -32602, 'INVALID_REQUEST_METADATA') if 'id' in request else None
        if 'progressToken' in metadata and (type(metadata['progressToken']) not in (str, int, float)
                or type(metadata['progressToken']) is bool):
            return self.error(identity, -32602, 'INVALID_PROGRESS_TOKEN') if 'id' in request else None
        if 'id' not in request:
            if method == 'notifications/initialized' and self.initialized: self.ready = True
            return None
        if method == 'ping': return {'jsonrpc': '2.0', 'id': identity, 'result': {}}
        if method == 'initialize':
            client = params.get('clientInfo')
            if (self.initialized or type(params.get('protocolVersion')) is not str
                    or type(params.get('capabilities')) is not dict or type(client) is not dict
                    or type(client.get('name')) is not str or not 1 <= len(client['name']) <= 256
                    or type(client.get('version')) is not str or not 1 <= len(client['version']) <= 64):
                return self.error(identity, -32602, 'INVALID_INITIALIZATION')
            self.initialized = True
            return {'jsonrpc': '2.0', 'id': identity, 'result': {'protocolVersion': PROTOCOL,
                    'capabilities': {'tools': {'listChanged': False}}, 'serverInfo': {'name': VERSION, 'version': '1.0.0'},
                    'instructions': 'Internal cached metadata/readiness reports. No live retrieval, molecular experiment or external delivery.'}}
        if not self.ready: return self.error(identity, -32002, 'INITIALIZATION_REQUIRED')
        if method == 'tools/list':
            if params: return self.error(identity, -32602, 'UNSUPPORTED_LIST_PARAMS')
            return {'jsonrpc': '2.0', 'id': identity, 'result': {'tools': TOOLS}}
        if method != 'tools/call': return self.error(identity, -32601, 'METHOD_NOT_FOUND')
        if set(params) - {'name', 'arguments'} or type(params.get('name')) is not str or type(params.get('arguments', {})) is not dict:
            return self.error(identity, -32602, 'INVALID_TOOL_PARAMS')
        if params['name'] not in {t['name'] for t in TOOLS}:
            return self.error(identity, -32602, 'UNKNOWN_TOOL')
        try:
            value = self.portfolio.call(params['name'], params.get('arguments', {}))
            result = {'content': [{'type': 'text', 'text': json.dumps(value, sort_keys=True, allow_nan=False)}],
                      'structuredContent': value, 'isError': False}
        except Exception as error:
            # Never return parser/source bodies, paths, credentials or exception text.
            result = {'content': [{'type': 'text', 'text': 'METADATA_TOOL_REJECTED'}], 'isError': True}
        return {'jsonrpc': '2.0', 'id': identity, 'result': result}


def serve(portfolio, input_stream, output_stream):
    session = Session(portfolio)
    while True:
        raw = input_stream.readline(MAX_MESSAGE_BYTES + 1)
        if not raw: break
        oversized = len(raw) > MAX_MESSAGE_BYTES
        try:
            request = parse_message(raw)
            response = session.handle(request)
        except Exception:
            response = session.error(None, -32700, 'PARSE_ERROR')
        if response is not None:
            output_stream.write(json.dumps(response, sort_keys=True, allow_nan=False) + '\n')
            output_stream.flush()
        if oversized: break  # Do not reinterpret an oversized message tail.


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--source-root', type=Path, required=True)
    p.add_argument('--registry', type=Path, required=True)
    p.add_argument('--workspace', type=Path, required=True)
    args = p.parse_args()
    app = Portfolio(args.source_root, args.registry, args.workspace)
    try: serve(app, sys.stdin.buffer, sys.stdout)
    finally: app.close()


if __name__ == '__main__': main()
