import json
from dnslib import DNSRecord, RR, QTYPE, A, AAAA, NS, PTR, DNSError
import socket
import time


class DNServer:
    main_server = "8.8.8.8"

    def __init__(self, host):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((host, 53))
        self.q_type = None
        self.transport = None
        self.cache = self.get_cache_from_json()

    def run(self):
        while True:
            data, addr = self.sock.recvfrom(1024)
            dns_request = DNSRecord.parse(data)
            q_name = dns_request.q.qname
            self.q_type = dns_request.q.qtype

            if q_name.__str__() + " " + self.q_type.__str__() in self.cache:
                reply = self.get_result_from_cache(dns_request, q_name)
                if reply.a.rdata:
                    self.sock.sendto(reply.pack(), addr)
                    continue
                else:
                    del self.cache[q_name.__str__() + " " + self.q_type.__str__()]

            reply = self.lookup(dns_request, self.main_server)
            self.cache_result(q_name, DNSRecord.parse(reply))
            self.sock.sendto(reply, addr)
            self.save_cache(self.cache)

    def get_result_from_cache(self, dns_record, q_name):
        reply = dns_record.reply()
        current_time = time.time()
        for answer in self.cache[q_name.__str__() + " " + self.q_type.__str__()]:
            if answer[2] + answer[1] >= current_time:
                match self.q_type:
                    case QTYPE.A:
                        rr = RR(rname=q_name, rtype=QTYPE.A,
                                rdata=A(answer[0]), ttl=answer[1])
                    case QTYPE.AAAA:
                        rr = RR(rname=q_name, rtype=QTYPE.AAAA,
                                rdata=AAAA(answer[0]), ttl=answer[1])
                    case QTYPE.NS:
                        rr = RR(rname=q_name, rtype=QTYPE.NS,
                                rdata=NS(answer[0]), ttl=answer[1])
                    case QTYPE.PTR:
                        rr = RR(rname=q_name, rtype=QTYPE.PTR,
                                rdata=PTR(answer[0]), ttl=answer[1])
                reply.add_answer(rr)
        return reply

    def cache_result(self, request, result: DNSRecord):
        answers = []
        for rr in result.rr:
            answers.append((rr.rdata.__str__(), rr.ttl, time.time()))
        if len(answers) == 0:
            return
        self.cache[request.__str__() + " " + self.q_type.__str__()] = answers

    def lookup(self, dns_record: DNSRecord, zone_ip):
        response = dns_record.send(zone_ip)
        parsed_response = DNSRecord.parse(response)
        if dns_record.header.id != parsed_response.header.id:
            raise DNSError(
                'Response transaction id does not match query transaction id')
        for address in parsed_response.auth:
            if address.rtype == 6:
                return response
        if parsed_response.a.rdata:
            return response
        new_zones_ip = self.get_new_ip(parsed_response)
        for new_zone_ip in new_zones_ip:
            ip = self.lookup(dns_record, new_zone_ip)
            if ip:
                return ip
        return None

    def get_new_ip(self, parsed_response):
        new_zones_ip = []
        for adr in parsed_response.ar:
            if adr.rtype == 1:
                new_zones_ip.append(adr.rdata.__repr__())
        if len(new_zones_ip) == 0:
            for adr in parsed_response.auth:
                if adr.rtype == 2:
                    question = DNSRecord.question(adr.rdata.__repr__())
                    pkt = self.lookup(question, self.main_server)
                    parsed_pkt = DNSRecord.parse(pkt)
                    new_zone_ip = parsed_pkt.a.rdata.__repr__()
                    if new_zone_ip:
                        new_zones_ip.append(new_zone_ip)
        return new_zones_ip

    @staticmethod
    def save_cache(data):
        with open("cache.json", 'w') as file:
            json.dump(data, file, indent=4)

    @staticmethod
    def get_cache_from_json():
        try:
            with open("cache.json", 'r') as file:
                data = json.load(file)
            return data
        except FileNotFoundError:
            return {}


if __name__ == "__main__":
    DNServer('127.0.0.1').run()
