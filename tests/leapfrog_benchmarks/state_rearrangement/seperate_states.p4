// HEADER START
#include <core.p4>
// HEADER END

header ip_t {
    bit<64> data;
}

header udp_t {
    bit<32> data;
}

header tcp_t {
    bit<64> data;
}

struct headers_t {
    ip_t ip;
    udp_t udp;
    tcp_t tcp;
}

parser Parser(packet_in pkt, out headers_t hdr) {
    state start {
        pkt.extract(hdr.ip);
        transition select(hdr.ip.data[43:40]) {
            (0001): parse_udp;
            (0000): parse_tcp;
        }
    }

    state parse_udp {
        pkt.extract(hdr.udp);
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
