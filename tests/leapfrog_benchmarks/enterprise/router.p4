// HEADER START
#include <core.p4>
// HEADER END

header HdrEth_t    { bit<112> data; }
header HdrVLAN0_t  { bit<160> data; }
header HdrVLAN1_t  { bit<160> data; }
header HdrIPv4_t   { bit<128>  data; }
header HdrIPv6_t   { bit<64>  data; }
header HdrTCP_t    { bit<160> data; }
header HdrUDP_t    { bit<160> data; }
header HdrICMP_t   { bit<32>  data; }
header HdrICMPv6_t { bit<32>  data; }
header HdrARP_t    { bit<64>  data; }
header HdrARPIP_t  { bit<64>  data; }

struct headers_t {
  HdrEth_t     eth;
  HdrVLAN0_t   vlan0;
  HdrVLAN1_t   vlan1;
  HdrIPv4_t    ipv4;
  HdrIPv6_t    ipv6;
  HdrTCP_t     tcp;
  HdrUDP_t     udp;
  HdrICMP_t    icmp;
  HdrICMPv6_t  icmpv6;
  HdrARP_t     arp;
  HdrARPIP_t   arpip;
}

parser Parser(packet_in pkt, out headers_t hdr) {
  state start {
    pkt.extract(hdr.eth);
    transition select(hdr.eth.data[111:96]) {
      0x8100: ParseVLAN0;
      0x9100: ParseVLAN0;
      0x9200: ParseVLAN0;
      0x9300: ParseVLAN0;
      0x0800: ParseIPv4;
      0x86dd: ParseIPv6;
      0x0806: ParseARP;
      0x8035: ParseARP;
      default: reject;
    }
  }

  state ParseVLAN0 {
    pkt.extract(hdr.vlan0);
    transition select(hdr.vlan0.data[159:144]) {
      0x8100: ParseVLAN1;
      0x9100: ParseVLAN1;
      0x9200: ParseVLAN1;
      0x9300: ParseVLAN1;
      0x0800: ParseIPv4;
      0x86dd: ParseIPv6;
      0x0806: ParseARP;
      0x8035: ParseARP;
      default: reject;
    }
  }

  state ParseVLAN1 {
    pkt.extract(hdr.vlan1);
    transition select(hdr.vlan1.data[159:144]) {
      0x0800: ParseIPv4;
      0x86dd: ParseIPv6;
      0x0806: ParseARP;
      0x8035: ParseARP;
      default: reject;
    }
  }

  state ParseIPv4 {
    pkt.extract(hdr.ipv4);
    transition select(hdr.ipv4.data[79:72]) {
      0x01: ParseICMP;
      0x06: ParseTCP;
      0x11: ParseUDP;
      default: accept;
    }
  }

  state ParseIPv6 {
    pkt.extract(hdr.ipv6);
    transition select(hdr.ipv6.data[55:48]) {
      0x01: ParseICMPv6;
      0x06: ParseTCP;
      0x11: ParseUDP;
      default: accept;
    }
  }

  state ParseTCP {
    pkt.extract(hdr.tcp);
    transition accept;
  }

  state ParseUDP {
    pkt.extract(hdr.udp);
    transition accept;
  }

  state ParseICMP {
    pkt.extract(hdr.icmp);
    transition accept;
  }

  state ParseICMPv6 {
    pkt.extract(hdr.icmpv6);
    transition accept;
  }

  state ParseARP {
    pkt.extract(hdr.arp);
    transition select(hdr.arp.data[31:16]) {
      0x0800: ParseARPIP;
      default: accept;
    }
  }

  state ParseARPIP {
    pkt.extract(hdr.arpip);
    transition accept;
  }
}

// FOOTER START
parser Parser_t(packet_in pkt, out headers_t hdr);
package Package(Parser_t p);

Package(Parser()) main;
// FOOTER END
