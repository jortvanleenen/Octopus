// HEADER START
#include <core.p4>
// HEADER END

header mpls_t {
    bit<32> label;
}

header udp_t {
    bit<64> data;
}

header test_t {
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
        transition select(hdr.mpls.label) {
            0: accept;          // terminating path
            default: loop;      // potential infinite loop
        }
    }

    state loop {
        /* no extract -> no progress */
        transition loop;
    }
}

// FOOTER START
parser Parser_t(packet_in pkt, out headers_t hdr);
package Package(Parser_t p);

Package(Parser()) main;
// FOOTER END