// HEADER START
#include <core.p4>
// HEADER END

header ip_t {
    bit<64> data;
}

header data_t {
    bit<32> data;
}

struct headers_t {
    ip_t ip;
    data_t pref;
    data_t suff;
}

parser Parser(packet_in pkt, out headers_t hdr) {
    state start {
        pkt.extract(hdr.ip);
        pkt.extract(hdr.pref);
        transition select(hdr.ip.data[43:40]) {
            (0001): accept;
            (0000): parse_suff;
        }
    }

    state parse_suff {
        pkt.extract(hdr.suff);
        transition accept;
    }
}

// FOOTER START
parser Parser_t(packet_in pkt, out headers_t hdr);
package Package(Parser_t p);

Package(Parser()) main;
// FOOTER END
