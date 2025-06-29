// HEADER START
#include <core.p4>
// HEADER END

header mpls_t  { bit<32> label; }
header udp_t   { bit<64> data; }

struct headers_t {
    mpls_t  mpls;
    udp_t   udp;
    mpls_t  temp;
}

parser Parser(packet_in pkt, out headers_t hdr) {
    state start {
        pkt.extract(hdr.mpls);
        hdr.temp.label = hdr.mpls.label >> 8 & 0x1;
        transition select(hdr.temp.label) {
            0: start;
            1: parse_udp;
        }
    }

    state parse_udp {
        pkt.extract(hdr.udp);
        transition accept;
    }
}

// FOOTER START
parser Parser_t(packet_in pkt, out headers_t hdr);
package Package(Parser_t p);

Package(Parser()) main;
// FOOTER END
