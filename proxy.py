from mitmproxy import http
import json
from time import sleep
import subprocess

socat_procs = None

def start_tcp_mitm(host):
    global socat_procs
    cmd = f"socat openssl-listen:443,reuseaddr,fork,cert=ssl/server.pem,cafile=ssl/server.crt,verify=0 tcp:127.0.0.1:8088"
    cmd2 = f"socat tcp-listen:8088,reuseaddr,fork openssl-connect:{host},verify=0"
    ps = subprocess.Popen(cmd, shell=True)
    ps2 = subprocess.Popen(cmd2, shell=True)
    socat_procs = (ps, ps2)
    print("[mitmproxy] socat tcp proxy started")

def response(flow: http.HTTPFlow) -> None:
        if flow.request.pretty_url.endswith("liveview"):
                print(f"[mitmproxy] Captured liveview request: {flow.response.text}")

                data = json.loads(flow.response.get_text())
                immi_url = data['server']
                immi_host = immi_url.split('immis://')[1].split('/')[0]
                flow.response.text = flow.response.text.replace(immi_host, '192.168.0.192:443')

                if socat_procs is not None:
                       socat_procs[0].kill()
                       socat_procs[1].kill()

                start_tcp_mitm(immi_host)

                #wait for socat to launch
                sleep(2)