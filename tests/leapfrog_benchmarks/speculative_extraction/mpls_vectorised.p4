// HEADER START
#include <core.p4>
// HEADER END

header udp_t  { bit<64> data; }
header tmp_t  { bit<32> field; }

struct headers_t {
    udp_t  udp;
    tmp_t  tmp;
    tmp_t  old;
    tmp_t  new;
}

parser Parser(packet_in pkt, out headers_t hdr) {
    state start {
        pkt.extract(hdr.old);
        pkt.extract(hdr.new);
        transition select(hdr.old.field[8:8], hdr.new.field[8:8]) {
            (0, 0): start;
            (0, 1): parse_udp;
            (1, _): cleanup;
        }
    }

    state parse_udp {
        pkt.extract(hdr.udp);
        transition accept;
    }

    state cleanup {
        pkt.extract(hdr.tmp);
        hdr.udp.data = hdr.new.field ++ hdr.tmp.field;
        transition accept;
    }
}

// FOOTER START
parser Parser_t(packet_in pkt, out headers_t hdr);
package Package(Parser_t p);

Package(Parser()) main;
// FOOTER END