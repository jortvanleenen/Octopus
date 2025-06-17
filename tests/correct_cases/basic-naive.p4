// HEADER START
#include <core.p4>
// HEADER END

header mpls_t {
    bit<2> label;
}

header udp_t {
    bit<2> data;
}

struct test_t {
    bit<2> field;
}

struct headers_t {
    mpls_t mpls;
    udp_t udp;
    test_t test;
}

parser Parser(packet_in pkt, out headers_t hdr) {
    state start {
        pkt.extract(hdr.mpls);
        hdr.mpls.label[1:0] = hdr.mpls.label[0:0] ++ hdr.mpls.label[1:1];
        transition select(hdr.mpls.label[0:0], hdr.mpls.label[1:1]) {
            (0, 0): start;
            (1, _): q2;
            default: accept;
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
