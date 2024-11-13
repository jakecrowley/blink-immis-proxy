from typing import Optional
from mitmproxy import ctx
from mitmproxy import http
import json
from time import sleep
import subprocess

class TCPMITM:
    def load(self, loader):
          self.socat_procs = None

          loader.add_option(
                name="tcp_bind_ip",
                typespec=Optional[str],
                default=None,
                help="socat bind ip"
          )

    def configure(self, updates):
        if ctx.options.tcp_bind_ip is None:
            raise Exception("You must set tcp_bind_ip!")

    def start_tcp_mitm(self, bind, host):
        global socat_procs
        cmd = f"socat openssl-listen:443,bind={bind},reuseaddr,fork,cert=ssl/server.pem,cafile=ssl/server.crt,verify=0 tcp:127.0.0.1:8088"
        cmd2 = f"socat tcp-listen:8088,reuseaddr,fork openssl-connect:{host},verify=0"
        ps = subprocess.Popen(cmd, shell=True)
        ps2 = subprocess.Popen(cmd2, shell=True)
        socat_procs = (ps, ps2)
        print("[mitmproxy] socat tcp proxy started")

    def response(self, flow: http.HTTPFlow) -> None:
            if flow.request.pretty_url.endswith("liveview"):
                    print(f"[mitmproxy] Captured liveview request: {flow.response.text}")

                    data = json.loads(flow.response.get_text())
                    immi_url = data['server']
                    immi_host = immi_url.split('immis://')[1].split('/')[0]
                    flow.response.text = flow.response.text.replace(immi_host, f'{ctx.options.tcp_bind_ip}:443')

                    if self.socat_procs is not None:
                        socat_procs[0].kill()
                        socat_procs[1].kill()

                    self.start_tcp_mitm(ctx.options.tcp_bind_ip, immi_host)

                    #wait for socat to launch
                    sleep(2)

addons = [TCPMITM()]