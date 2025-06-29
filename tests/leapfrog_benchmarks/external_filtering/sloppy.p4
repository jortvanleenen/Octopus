// HEADER START
#include <core.p4>
// HEADER END

header eth_t   { bit<112> data; }
header ipv4_t  { bit<128> data; }
header ipv6_t  { bit<288> data; }

struct headers_t {
    eth_t   eth;
    ipv4_t  ipv4;
    ipv6_t  ipv6;
}

parser Parser(packet_in pkt, out headers_t hdr) {
    state start {
        pkt.extract(hdr.eth);
        transition select(hdr.eth.data[15:0]) {
            0x86dd: parse_ipv6;
            default: parse_ipv4;
        }
    }

    state parse_ipv4 {
        pkt.extract(hdr.ipv4);
        transition accept;
    }

    state parse_ipv6 {
        pkt.extract(hdr.ipv6);
        transition accept;
    }
}

// FOOTER START
parser Parser_t(packet_in pkt, out headers_t hdr);
package Package(Parser_t p);

Package(Parser()) main;
// FOOTER END
