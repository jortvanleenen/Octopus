// HEADER START
#include <core.p4>
// HEADER END

header eth_t     { bit<112> data; }
header vlan_t    { bit<160> data; }
header ipv4_t    { bit<160> data; }
header icmp_t    { bit<32> data; }
header tcp_t     { bit<160> data; }
header udp_t     { bit<160> data; }
header gre_t     { bit<32> data; }
header nvgre_t   { bit<32> data; }
header vxlan_t   { bit<64> data; }
header arp_t     { bit<64> data; }
header arp_ip_t  { bit<160> data; }

struct headers_t {
    eth_t     eth0;
    eth_t     eth1;
    vlan_t    vlan0;
    vlan_t    vlan1;
    ipv4_t    ipv4;
    icmp_t    icmp;
    tcp_t     tcp;
    udp_t     udp;
    gre_t     gre0;
    gre_t     gre1;
    gre_t     gre2;
    nvgre_t   nvgre;
    vxlan_t   vxlan;
    arp_t     arp;
    arp_ip_t  arp_ip;
}

parser Parser(packet_in pkt, out headers_t hdr) {
    state start {
        pkt.extract(hdr.eth0);
        transition select(hdr.eth0.data[15:0]) {
            0x8100: parse_vlan0;
            0x9100: parse_vlan0;
            0x9200: parse_vlan0;
            0x9300: parse_vlan0;
            0x0800: parse_ipv4;
            0x0806: parse_arp;
            0x8035: parse_arp;
            default: reject;
        }
    }

    state parse_vlan0 {
        pkt.extract(hdr.vlan0);
        transition select(hdr.vlan0.data[15:0]) {
            0x8100: parse_vlan1;
            0x9100: parse_vlan1;
            0x9200: parse_vlan1;
            0x9300: parse_vlan1;
            0x0800: parse_ipv4;
            0x0806: parse_arp;
            0x8035: parse_arp;
            default: reject;
        }
    }

    state parse_vlan1 {
        pkt.extract(hdr.vlan1);
        transition select(hdr.vlan1.data[15:0]) {
            0x0800: parse_ipv4;
            0x0806: parse_arp;
            0x8035: parse_arp;
            default: reject;
        }
    }

    state parse_ipv4 {
        pkt.extract(hdr.ipv4);
        transition select(hdr.ipv4.data[87:80]) {
            6: parse_tcp;
            17: parse_udp;
            47: parse_gre0;
            default: accept;
        }
    }

    state parse_tcp {
        pkt.extract(hdr.tcp);
        transition accept;
    }

    state parse_udp {
        pkt.extract(hdr.udp);
        transition select(hdr.udp.data[143:128]) {
            0xFFFF: parse_vxlan;
            default: accept;
        }
    }

    state parse_icmp {
        pkt.extract(hdr.icmp);
        transition accept;
    }

    state parse_gre0 {
        pkt.extract(hdr.gre0);
        transition select(hdr.gre0.data[29:29], hdr.gre0.data[15:0]) {
            (1, 0x6558): parse_nvgre;
            (1, 0x6559): parse_gre1;
            default: accept;
        }
    }

    state parse_gre1 {
        pkt.extract(hdr.gre1);
        transition select(hdr.gre1.data[15:0]) {
            0x16558: parse_nvgre;
            0x16559: parse_gre2;
            default: accept;
        }
    }

    state parse_gre2 {
        pkt.extract(hdr.gre2);
        transition select(hdr.gre2.data[15:0]) {
            0x16558: parse_nvgre;
            0x16559: reject;
            default: accept;
        }
    }

    state parse_nvgre {
        pkt.extract(hdr.nvgre);
        transition parse_eth1;
    }

    state parse_vxlan {
        pkt.extract(hdr.vxlan);
        transition parse_eth1;
    }

    state parse_eth1 {
        pkt.extract(hdr.eth1);
        transition accept;
    }

    state parse_arp {
        pkt.extract(hdr.arp);
        transition select(hdr.arp.data[47:32]) {
            0x0800: parse_arp_ip;
            default: accept;
        }
    }

    state parse_arp_ip {
        pkt.extract(hdr.arp_ip);
        transition accept;
    }
}

// FOOTER START
parser Parser_t(packet_in pkt, out headers_t hdr);
package Package(Parser_t p);

Package(Parser()) main;
// FOOTER END
