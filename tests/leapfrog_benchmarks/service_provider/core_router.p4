// HEADER START
#include <core.p4>
// HEADER END

header eth_t     { bit<112> data; }
header mpls_t    { bit<32> data; }
header ip_ver_t  { bit<4> data; }
header ihl_t     { bit<4> data; }
header ipv4_5_t  { bit<152> data; }
header ipv4_6_t  { bit<184> data; }
header ipv4_7_t  { bit<216> data; }
header ipv4_8_t  { bit<248> data; }
header ipv6_t    { bit<316> data; }

struct headers_t {
    eth_t     eth;
    mpls_t    mpls;
    ip_ver_t  ip_ver;
    ihl_t     ihl;
    ipv4_5_t  ipv4_5;
    ipv4_6_t  ipv4_6;
    ipv4_7_t  ipv4_7;
    ipv4_8_t  ipv4_8;
    ipv6_t    ipv6;
}

parser Parser(packet_in pkt, out headers_t hdr) {
    state start {
        pkt.extract(hdr.eth);
        transition select(hdr.eth.data[111:96]) {
            0x8847: parse_mpls;
            0x8848: parse_mpls;
            0x0800: parse_ethv4;
            0x86dd: parse_ethv6;
            default: reject;
        }
    }

    state parse_ethv4 {
        pkt.extract(hdr.ip_ver);
        transition parse_ipv4;
    }

    state parse_ethv6 {
        pkt.extract(hdr.ip_ver);
        transition parse_ipv6;
    }

    state parse_mpls {
        pkt.extract(hdr.mpls);
        transition select(hdr.mpls.data[24:24]) {
            0: parse_mpls;
            1: parse_ip_ver;
            default: reject;
        }
    }

    state parse_ip_ver {
        pkt.extract(hdr.ip_ver);
        transition select(hdr.ip_ver.data) {
            4: parse_ipv4;
            6: parse_ipv6;
            default: reject;
        }
    }

    state parse_ipv4 {
        pkt.extract(hdr.ihl);
        transition select(hdr.ihl.data) {
            5: parse_ipv4_5;
            6: parse_ipv4_6;
            7: parse_ipv4_7;
            8: parse_ipv4_8;
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
