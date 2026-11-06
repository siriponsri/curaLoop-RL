"""Bound the transport used by unchanged skill clients; never emit response snippets."""

import hashlib
import json
import math
import time
from types import SimpleNamespace
from urllib.parse import urlsplit

import requests

from .contracts import QualificationError


def spec_key(path, params):
    return path, json.dumps(params, sort_keys=True, separators=(',', ':'), allow_nan=False)


class BoundedTransport:
    def __init__(self, base_url, specifications, maximum_requests, byte_limit, cumulative_limit,
                 interval=1.1, session_factory=requests.Session):
        if base_url not in ('https://pubchem.ncbi.nlm.nih.gov/rest/pug', 'https://rest.uniprot.org'):
            raise QualificationError('Unsupported service origin')
        if (any(type(v) is not int for v in (maximum_requests, byte_limit, cumulative_limit))
                or not 0 < byte_limit <= cumulative_limit <= 256 * 1024**2 or not 0 < maximum_requests <= 96
                or type(interval) not in (int, float) or not math.isfinite(interval) or interval < 0):
            raise QualificationError('Invalid request/byte envelope')
        self.base_url = base_url
        self.allowed = {spec_key(row['path'], row.get('params', {})) for row in specifications}
        self.maximum_requests, self.byte_limit, self.cumulative_limit = maximum_requests, byte_limit, cumulative_limit
        self.interval, self.session_factory = interval, session_factory
        self.attempts, self.total_bytes, self.previous = [], 0, None
        self.failed = False

    def bind(self, client):
        # The client's source remains unchanged. Its exact execute() calls this
        # isolated requests-compatible boundary rather than unrestricted transport.
        client.requests = SimpleNamespace(Session=lambda: SafeSession(self), RequestException=requests.RequestException)
        return client


class SafeSession:
    def __init__(self, guard):
        self.guard = guard
        self.real = guard.session_factory()
        self.real.trust_env = False
        self.headers = self.real.headers

    def close(self):
        self.real.close()

    def request(self, method, url, **kwargs):
        guard = self.guard
        if guard.failed or guard.total_bytes >= guard.cumulative_limit:
            raise QualificationError('Transport stopped after failure or cumulative exhaustion')
        base = guard.base_url
        parts = urlsplit(url)
        if (method != 'GET' or parts.scheme != 'https' or parts.username or parts.password
                or parts.query or parts.fragment or not url.startswith(base + '/')
                or parts.netloc != urlsplit(base).netloc):
            raise QualificationError('Unsupported request origin/method')
        path = url[len(base) + 1:]
        params = kwargs.get('params', {})
        if spec_key(path, params) not in guard.allowed:
            raise QualificationError('Request differs from frozen exact allowlist')
        if set(kwargs) - {'params', 'timeout'} or not 0 < kwargs.get('timeout', 0) <= 30:
            raise QualificationError('Unsupported request options')
        if len(guard.attempts) >= guard.maximum_requests:
            raise QualificationError('Request count exhausted')
        if guard.previous is not None:
            time.sleep(max(0., guard.interval - (time.monotonic() - guard.previous)))
        guard.previous = time.monotonic()
        record = {'path': path, 'params': params, 'method': method, 'status': 'STARTED',
                  'decoded_bytes_observed': 0, 'redirects_allowed': False}
        guard.attempts.append(record)
        response = None
        try:
            response = self.real.request(method, url, **kwargs, stream=True, allow_redirects=False)
            record['http_status'] = response.status_code
            record['headers'] = {k: v for k, v in response.headers.items()
                                 if k.lower() in ('content-type', 'content-length', 'x-uniprot-release',
                                                  'x-uniprot-release-date', 'x-total-results')}
            if 300 <= response.status_code < 400:
                raise QualificationError('Redirect rejected')
            response.raise_for_status()
            content_type = response.headers.get('content-type', '').lower()
            if 'html' in content_type:
                raise QualificationError('HTML response rejected')
            chunks, digest = [], hashlib.sha256()
            for chunk in response.iter_content(chunk_size=64 * 1024):
                if not chunk:
                    continue
                guard.total_bytes += len(chunk)
                record['decoded_bytes_observed'] += len(chunk)
                if record['decoded_bytes_observed'] > guard.byte_limit or guard.total_bytes > guard.cumulative_limit:
                    raise QualificationError('Decoded response byte ceiling exceeded')
                digest.update(chunk)
                chunks.append(chunk)
            data = b''.join(chunks)
            data.decode('utf-8', errors='strict')
            response._content, response._content_consumed = data, True
            response.encoding = 'utf-8'
            record.update(status='BOUNDED_RESPONSE', decoded_sha256=digest.hexdigest())
            return response
        except Exception as error:
            guard.failed = True
            record.update(status='FAILED', error_type=type(error).__name__)
            raise
        finally:
            if response is not None:
                response.close()
