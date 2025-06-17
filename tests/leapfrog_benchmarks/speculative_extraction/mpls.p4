// HEADER START
#include <core.p4>
// HEADER END

header mpls_t {
    bit<32> label;
    data 16
    tag 16
}

header udp_t {
    bit<64> data;
}

struct headers_t {
    mpls_t mpls;
    udp_t udp;
}

parser Parser(packet_in pkt, out headers_t hdr) {
    state start {
        pkt.extract(hdr.mpls);
        transition select(hdr.mpls.label[1:1]) {
            (0): start;
            (1): q2;
        }
    }

    state q2 {
        pkt.extract(hdr.udp);
        transition accept;
    }
}

// FOOTER START
parser Parser_t(packet_in pkt, out headers_t hdr);
package Package(Parser_t p);

Package(Parser()) main;
// FOOTER END
