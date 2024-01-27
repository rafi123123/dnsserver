#!/usr/bin/env python
import argparse
import sys
import time
import threading
import socketserver
import re
import logging
try:
    from dnslib import A, DNSRecord, DNSHeader, QTYPE, RR, DNSError
except ImportError:
    print("Missing dependency dnslib: <https://pypi.python.org/pypi/dnslib>. Please install it with `pip`.")
    sys.exit(2)


import logging, sys

logger = logging.getLogger("main")
logger.setLevel(logging.DEBUG)

file_formatter = logging.Formatter("[%(levelname)s]::%(asctime)s::func[%(funcName)s:%(lineno)d]::file[%(filename)s]::PID[%(process)d]::ProcessName[%(processName)s]::%(message)s")
file_handler = logging.FileHandler("dns_server.log")
file_handler.setFormatter(file_formatter)
file_handler.setLevel(logging.DEBUG)
logger.addHandler(file_handler)

short_formatter = logging.Formatter("%(asctime)s: %(message)s")
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(short_formatter)
logger.addHandler(console_handler)


class BaseRequestHandler(socketserver.BaseRequestHandler):

    def get_data(self):
        raise NotImplementedError

    def send_data(self, data):
        raise NotImplementedError

    def handle(self):
        data = self.get_data()
        self.send_data(dns_response(data))

class UDPRequestHandler(BaseRequestHandler):
    def get_data(self):
        return self.request[0].strip()

    def send_data(self, data):
        return self.request[1].sendto(data, self.client_address)


def dns_response(data):
    TTL = 600
    try:
        request = DNSRecord.parse(data)
    except DNSError:
        logger.warning(f"[-] Invalid DNS request received: {data}")
    reply = DNSRecord(DNSHeader(id=request.header.id, qr=1, aa=1, ra=1), q=request.q)
    dn = str(request.q.qname).lower()
    domain_match = re.match("(?:(.*?)\.)?(?:(\d{0,3}\.\d{0,3}\.\d{0,3}\.\d{0,3})\.target\.)?(\d{0,3}\.\d{0,3}\.\d{0,3}\.\d{0,3})\.ns\.rebindmultia\.com", dn)
    if not domain_match:
        #Not a request we are interested in responding to
        return reply.pack()
    domain_id, target_server, my_ip = domain_match.groups()
    qname = request.q.qname
    if target_server: return_server = target_server
    else: return_server = my_ip
    reply.add_answer(RR(rname=qname, rtype=QTYPE.A, rclass=1, ttl=TTL, rdata=A(return_server)))
    logger.info(f"[+] {domain_id} - A:{return_server}")
    return reply.pack()



def main(args):
    logger.info(f"[+] Starting DNS server on port {args.dns_port}")
    s = socketserver.ThreadingUDPServer(('0.0.0.0', int(args.dns_port)), UDPRequestHandler)
    thread = threading.Thread(target=s.serve_forever)
    thread.daemon = True
    thread.start()

    try:
        while 1:
            time.sleep(1)
            sys.stderr.flush()
            sys.stdout.flush()

    except KeyboardInterrupt:
        pass
    finally:
        logger.info("[-] Shutting down DNS server")
        s.shutdown()
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--dns-port', help="Specify the DNS server port. Default: 53", default=53)
    args = parser.parse_args()
    main(args)
