import argparse
import frida
import time

tls_verify_hook = """
Java.perform(() => {
    var walnuthelper = Java.use('com.immediasemi.walnut.internal.LibraryHelper');
    var walnut = walnuthelper.$new();

    console.log("[interceptor] Loaded", walnut.libraryVersionString());

    var libwalnutso = 0;
    while (libwalnutso < 0xf) {
        libwalnutso = Module.findExportByName('libwalnut.so', 'mbedtls_x509_crt_verify_with_profile');
    }

    Interceptor.attach(libwalnutso, {
        onEnter: function(args) {}, 
        onLeave: function(retval) {
            console.log("[interceptor] mbedtls_x509_crt_verify_with_profile returned with " + retval + ", replacing with success");
            retval.replace(0);
        }
    });

    console.log("[interceptor] Hooked mbedtls_x509_crt_verify_with_profile")
});
"""

def main(android_ip: str):
    device = frida.get_device_manager().add_remote_device(android_ip)
    session = device.attach("Blink")
    script = session.create_script(tls_verify_hook)
    script.load()

    while not session.is_detached:
        time.sleep(1)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('android_ip', type=str)
    args = parser.parse_args()
    main(args.android_ip)
