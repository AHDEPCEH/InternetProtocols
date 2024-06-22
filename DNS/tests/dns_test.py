import unittest
from dnslib import DNSRecord, QTYPE
from unittest.mock import patch
from InternetProtocols.DNS.module.dnserver import DNServer


class TestDNServer(unittest.TestCase):

    def setUp(self):
        self.dns_server = DNServer("127.0.0.1")

    def test_get_result_from_cache(self):
        dns_record = DNSRecord()
        q_name = "example.com"
        q_type = QTYPE.A
        self.dns_server.cache = {f"{q_name} {q_type}": [("192.168.1.1", 3600, 1634070000.0)]}

        reply = self.dns_server.get_result_from_cache(dns_record, q_name)
        self.assertEqual(reply.a.rdata, "192.168.1.1")

    @patch('dns_server.socket.socket')
    def test_run(self, mock_socket):
        mock_socket.recvfrom.return_value = (b'', ('127.0.0.1', 53))
        with patch('dns_server.DNSRecord.parse') as mock_parse:
            mock_parse.return_value = DNSRecord()
            self.dns_server.run()

        # Add more test cases for other methods as needed


if __name__ == '__main__':
    unittest.main()
