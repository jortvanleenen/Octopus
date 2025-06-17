// HEADER START
#include <core.p4>
// HEADER END

header hdr_t {
    bit<4> hello;
}

struct headers_t {
    hdr_t octopus;
}

parser Parser(packet_in pkt, out headers_t hdr) {
    state start {
        pkt.extract(hdr.octopus);
        transition accept;
    }
}

// FOOTER START
parser Parser_t(packet_in pkt, out headers_t hdr);
package Package(Parser_t p);

Package(Parser()) main;
// FOOTER END
