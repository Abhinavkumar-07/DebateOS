import urllib.request
import json
import sys

def run():
    try:
        req = urllib.request.Request(
            'http://localhost:8000/debate/start',
            data=json.dumps({'claim':'AI is good','rounds':1}).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )
        res = urllib.request.urlopen(req).read().decode()
        debate_id = json.loads(res)['debate_id']
        print(f"Started debate: {debate_id}")

        print("Streaming...")
        res2 = urllib.request.urlopen(f'http://localhost:8000/debate/{debate_id}/stream')
        for line in res2:
            decoded = line.decode().strip()
            if decoded:
                print(decoded)
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    run()
