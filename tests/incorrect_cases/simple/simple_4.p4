// HEADER START
#include <core.p4>
// HEADER END

header mpls_t {
    bit<4> label;
}

struct headers_t {
    mpls_t mpls;
}

parser Parser(packet_in pkt, out headers_t hdr) {
    state start {
        pkt.extract(hdr.mpls);
        transition accept;
    }
}

// FOOTER START
parser Parser_t(packet_in pkt, out headers_t hdr);
package Package(Parser_t p);

Package(Parser()) main;
// FOOTER END
