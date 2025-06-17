// HEADER START
#include <core.p4>
// HEADER END

header eth_t { bit<112> data; }
header mpls_t { bit<32> data; }
header eompls_t { bit<28> data; }
header ipver_t { bit<4> data; }
header ipv4_5_t { bit<152> data; }
header ipv4_6_t { bit<184> data; }
header ipv4_7_t { bit<216> data; }
header ipv4_8_t { bit<248> data; }
header ipv6_t { bit<316> data; }

struct headers_t {
    eth_t eth0;
    eth_t eth1;
    mpls_t mpls0;
    mpls_t mpls1;
    eompls_t eompls;
    ipver_t ipver;
    ipv4_5_t ipv4_5;
    ipv4_6_t ipv4_6;
    ipv4_7_t ipv4_7;
    ipv4_8_t ipv4_8;
    ipv6_t ipv6;
}

parser Parser(packet_in pkt, out headers_t hdr) {
    state start {
        pkt.extract(hdr.eth0);
        transition select(hdr.eth0.data[111:96]) {
            (0x8857): parse_mpls0;
            (0x8868): parse_mpls0;
            (0x8020): ignore_ipver4;
            (0x886d): ignore_ipver6;
            default: accept;
        }
    }

    state parse_mpls0 {
        pkt.extract(hdr.mpls0);
        transition select(hdr.mpls0.data[23:23]) {
            (0b0): parse_mpls1;
            (0b1): parse_ipver;
            default: reject;
        }
    }

    state parse_mpls1 {
        pkt.extract(hdr.mpls1);
        transition select(hdr.mpls1.data[23:23]) {
            (0b1): parse_ipver;
            default: reject;
        }
    }

    state parse_ipver {
        pkt.extract(hdr.ipver);
        transition select(hdr.ipver.data) {
            (0x0): parse_eompls;
            (0x4): parse_ipv4;
            (0x6): parse_ipv6;
            default: reject;
        }
    }

    state ignore_ipver4 {
        pkt.extract(hdr.ipver);
        transition parse_ipv4;
    }

    state ignore_ipver6 {
        pkt.extract(hdr.ipver);
        transition parse_ipv6;
    }

    state parse_eompls {
        pkt.extract(hdr.eompls);
        transition parse_eth1;
    }

    state parse_eth1 {
        pkt.extract(hdr.eth1);
        transition accept;
    }

    state parse_ipv4 {
        pkt.extract(hdr.ipver);
        transition select(hdr.ipver.data) {
            (0x5): parse_ipv4_5;
            (0x6): parse_ipv4_6;
            (0x7): parse_ipv4_7;
            (0x8): parse_ipv4_8;
            default: reject;
        }
    }

    state parse_ipv4_5 {
        pkt.extract(hdr.ipv4_5);
        transition accept;
    }

    state parse_ipv4_6 {
        pkt.extract(hdr.ipv4_6);
        transition accept;
    }

    state parse_ipv4_7 {
        pkt.extract(hdr.ipv4_7);
        transition accept;
    }

    state parse_ipv4_8 {
        pkt.extract(hdr.ipv4_8);
        transition accept;
    }

    state parse_ipv6 {
        pkt.extract(hdr.ipv6);
        transition accept;
    }
}

// FOOTER START
parser Parser_t(packet_in pkt, out headers_t hdr);
package Package(Parser_t p);

Package(Parser()) main;
// FOOTER END
