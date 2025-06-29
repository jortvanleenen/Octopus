// HEADER START
#include <core.p4>
// HEADER END

header eth_t      { bit<112> data; }
header vlan_t     { bit<160> data; }
header ipv4_t     { bit<128>  data; }
header ipv6_t     { bit<64>  data; }
header tcp_t      { bit<160> data; }
header udp_t      { bit<160> data; }
header icmp_t     { bit<32>  data; }
header icmp_v6_t  { bit<32>  data; }
header arp_t      { bit<64>  data; }
header arp_ip_t   { bit<64>  data; }

struct headers_t {
    eth_t      eth;
    vlan_t     vlan0;
    vlan_t     vlan1;
    ipv4_t     ipv4;
    ipv6_t     ipv6;
    tcp_t      tcp;
    udp_t      udp;
    icmp_t     icmp;
    icmp_v6_t  icmp_v6;
    arp_t      arp;
    arp_ip_t   arp_ip;
}

parser Parser(packet_in pkt, out headers_t hdr) {
    state start {
        pkt.extract(hdr.eth);
        transition select(hdr.eth.data[111:96]) {
            0x8100: parse_vlan0;
            0x9100: parse_vlan0;
            0x9200: parse_vlan0;
            0x9300: parse_vlan0;
            0x0800: parse_ipv4;
            0x86dd: parse_ipv6;
            0x0806: parse_arp;
            0x8035: parse_arp;
            default: reject;
        }
    }

  state parse_vlan0 {
    pkt.extract(hdr.vlan0);
    transition select(hdr.vlan0.data[159:144]) {
      0x8100: parse_vlan1;
      0x9100: parse_vlan1;
      0x9200: parse_vlan1;
      0x9300: parse_vlan1;
      0x0800: parse_ipv4;
      0x86dd: parse_ipv6;
      0x0806: parse_arp;
      0x8035: parse_arp;
      default: reject;
    }
  }

  state parse_vlan1 {
    pkt.extract(hdr.vlan1);
    transition select(hdr.vlan1.data[159:144]) {
      0x0800: parse_ipv4;
      0x86dd: parse_ipv6;
      0x0806: parse_arp;
      0x8035: parse_arp;
      default: reject;
    }
  }

  state parse_ipv4 {
    pkt.extract(hdr.ipv4);
    transition select(hdr.ipv4.data[79:72]) {
      1: parse_icmp;
      6: parse_tcp;
      11: parse_udp;
      default: accept;
    }
  }

    state parse_ipv6 {
        pkt.extract(hdr.ipv6);
        transition select(hdr.ipv6.data[55:48]) {
            1: parse_icmp_v6;
            6: parse_tcp;
            11: parse_udp;
            default: accept;
        }
    }

    state parse_tcp {
        pkt.extract(hdr.tcp);
        transition accept;
    }

    state parse_udp {
        pkt.extract(hdr.udp);
        transition accept;
    }

    state parse_icmp {
        pkt.extract(hdr.icmp);
        transition accept;
    }

    state parse_icmp_v6 {
        pkt.extract(hdr.icmp_v6);
        transition accept;
    }

    state parse_arp {
        pkt.extract(hdr.arp);
        transition select(hdr.arp.data[31:16]) {
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
