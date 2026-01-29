// HEADER START
#include <core.p4>
// HEADER END

header eth_t  { bit<112> data; }
header vlan_t { bit<32> data; }
header ip_t   { bit<160> data; }
header udp_t  { bit<64> data; }

struct headers_t {
    eth_t  eth;
    vlan_t vlan;
    ip_t   ip;
    udp_t  udp;
}

parser Parser(packet_in pkt, out headers_t hdr) {
    state start {
        pkt.extract(hdr.eth);
        transition select(hdr.eth.data[111:111]) {
            0: default_vlan;
            1: parse_vlan;
        }
    }

    state default_vlan {
        hdr.vlan.data = 0;
        pkt.extract(hdr.ip);
        transition parse_udp;
    }

    state parse_vlan {
        pkt.extract(hdr.vlan);
        transition parse_ip;
    }

    state parse_ip {
        pkt.extract(hdr.ip);
        transition parse_udp;
    }

    state parse_udp {
        pkt.extract(hdr.udp);
        transition select(hdr.vlan.data[31:28]) {
            0b1111: reject;
            default: accept;
        }
    }
}

// FOOTER START
parser Parser_t(packet_in pkt, out headers_t hdr);
package Package(Parser_t p);

Package(Parser()) main;
// FOOTER END
