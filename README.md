# Blink IMMIS Proxy

Instructions are for Linux, not tested on Windows. If you do not have access to a physical rooted Android device, you can install Bliss OS in a virtual machine, I use QEMU/KVM and it works flawlessly. 

## Usage
1. Install python3-virtualenv, socat, and wireshark with your distro's package manager, e.g. `dnf install python3-virtualenv socat wireshark`
2. Clone repo and cd into its directory.
3. Create new virtualenv with `python -m venv .venv`
4. Enter the virtualenv with `source .venv/bin/activate`
5. Install dependencies with `pip install -r requirements.txt`
6. Connect ADB to device either remotely or via USB.
7. Launch frida-server on rooted android device with Blink app installed
8. Run `./start.sh <host ip> <android device ip>` e.g. `./start.sh 192.168.0.192 192.168.124.223`

    Note: On first run openssl will prompt you to fill out details for a self-signed certificate, you may leave all defaults.
    You may also need to run this script as root, as it listens on port 443 (libwalnut seems to not like if you try to connect to an immis stream on a different port)

9. Launch wireshark, listen on loopback (lo) interface, filter on `tcp.port == 8088`.