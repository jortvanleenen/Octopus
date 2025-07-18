// HEADER START
#include <core.p4>
// HEADER END

header mpls_t {
    bit<32> label;
}

header udp_t {
    bit<64> data;
}

struct test_t {
    bit<32> field;
}

struct headers_t {
    mpls_t mpls;
    udp_t udp;
    test_t test;
}

parser Parser(packet_in pkt, out headers_t hdr) {
    state start {
        pkt.extract(hdr.mpls);
        hdr.mpls.label = hdr.mpls.label[31:2] ++ hdr.mpls.label[0:0] ++ hdr.mpls.label[1:1];
        transition select(hdr.mpls.label[23:23], hdr.mpls.label[24:21]) {
            (0, 0x44): start;
            (_, 1): q2;
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
