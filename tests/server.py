from support import Fixture, run, verify_signature
import base64
import gzip
import json
from urllib.parse import parse_qs, unquote, urlsplit

class Handler(Fixture):

    def route(self, body):
        service = verify_signature(self, body)
        target = self.headers.get('X-Amz-Target', '').split('.')[-1]
        self.server.calls[target] = self.server.calls.get(target, 0) + 1
        assert service == 'ssm'
        data = json.loads(body)
        assert data['Name'] == '/test/雪'
        if target == 'PutParameter':
            assert data == {'Name': '/test/雪', 'Value': 'hello 😀', 'Type': 'SecureString', 'Overwrite': True}
            result = {'Version': 2}
        elif target == 'GetParameter':
            assert data['WithDecryption'] is True
            result = {'Parameter': {'Name': data['Name'], 'Type': 'SecureString', 'Value': 'hello 😀', 'Version': 2}}
        else:
            assert target == 'DeleteParameter'
            result = {}
        self.reply(200, result)
if __name__ == '__main__':
    run(Handler)
