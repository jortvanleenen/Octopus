// HEADER START
#include <core.p4>
// HEADER END

header udp_t { bit<16> src_port;  bit<16> dst_port;
               bit<16> length;    bit<16> checksum; }

header ip_t      { bit<64> data; }
header tcp_t     { bit<64> data; }
struct headers_t { ip_t ip; udp_t udp; tcp_t tcp; }

parser Parser(packet_in pkt, out headers_t hdr) {
    state start {
        pkt.extract(hdr.ip);
        transition select(hdr.ip.data[23:20]) {
            0: parse_tcp;
            1: parse_udp;
            _: reject;
        }
    }
    state parse_udp {
        pkt.extract(hdr.udp);
        hdr.udp.length =
            hdr.udp.length[7:0] ++ hdr.udp.length[15:8];
        transition accept;
    }
    state parse_tcp {
        pkt.extract(hdr.tcp);
        transition accept;
    }
}

// FOOTER START
parser Parser_t(packet_in pkt, out headers_t hdr);
package Package(Parser_t p);

Package(Parser()) main;
// FOOTER END
