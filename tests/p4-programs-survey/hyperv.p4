// HEADER START
#include <core.p4>
// HEADER END

// The original parser would always accept, but its syntax was no longer supported by the P4 language.
// Therefore, we have written an equivalent parser in P4_16.

header header_t  {
    bit<128> field;
}

struct headers_t {
    header_t head;
}

parser Parser(packet_in pkt, out headers_t hdr) {
    state start {
        pkt.extract(hdr.head);
        transition accept;
    }
}

// FOOTER START
parser Parser_t(packet_in pkt, out headers_t hdr);
package Package(Parser_t p);

Package(Parser()) main;
// FOOTER END
