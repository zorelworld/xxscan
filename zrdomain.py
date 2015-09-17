import socket
import sys
from wydomain_ip2domain import ip2domain_start
from wydomain_dirburster import start_attack

def start_zrdomain(domain):
    ip_c_block=domain
    r=ip2domain_start(ip_c_block)
    a=r.values()
    result=start_attack(a)
    for res in result:
        domains = res.get()
        print domains


if __name__ == "__main__":
    if len(sys.argv) == 2:
        print start_zrdomain(sys.argv[1])
        sys.exit(0)
    else:
        print ("usage: %s domain" % sys.argv[0])
        sys.exit(-1)