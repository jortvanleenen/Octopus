// HEADER START
#include <core.p4>
// HEADER END

header udp_t {
    bit<64> data;
}

header tmp_t {
    bit<32> field;
}

struct headers_t {
    udp_t udp;
    tmp_t tmp;
    tmp_t old;
    tmp_t new;
}

parser Parser(packet_in pkt, out headers_t hdr) {
    state start {
        pkt.extract(hdr.old);
        pkt.extract(hdr.new);
        transition select(hdr.old.field[1:1], hdr.new.field[1:1]) {
            (0, 0): start;
            (0, 1): q4;
            (1, _): q5;
        }
    }

    state q4 {
        pkt.extract(hdr.udp);
        transition accept;
    }

    state q5 {
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