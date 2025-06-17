// HEADER START
#include <core.p4>
// HEADER END

header ethernet_t {
    bit<112> data;
}

header ipv4_t {
    bit<128> data;
}

header ipv6_t {
    bit<288> data;
}

struct headers_t {
    ethernet_t eth;
    ipv4_t ipv4;
    ipv6_t ipv6;
}

parser Parser(packet_in pkt, out headers_t hdr) {
    state start {
        pkt.extract(hdr.eth);
        transition select(hdr.eth.data[111:96]) {
            (0x86dd): parse_ipv6;
            (0x8600): parse_ipv4;
            default: reject;
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
