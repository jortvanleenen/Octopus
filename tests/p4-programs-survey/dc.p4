/* -*- P4_16 -*- */

#include <core.p4>

// ======================= HEADERS =======================

header ethernet_t {
    bit<48> dstAddr;
    bit<48> srcAddr;
    bit<16> etherType;
}

header snap_header_t {
    bit<8>  dsap;
    bit<8>  ssap;
    bit<8>  control_;
    bit<24> oui;
    bit<16> type_;
}

header cpu_header_t {
    bit<3>  qid;
    bit<1>  pad;
    bit<12> reason_code;
    bit<16> rxhash;
    bit<16> bridge_domain;
    bit<16> ingress_lif;
    bit<16> egress_lif;
    bit<1>  lu_bypass_ingress;
    bit<1>  lu_bypass_egress;
    bit<14> pad1;
    bit<16> etherType;
}

header vlan_tag_t {
    bit<3>  pcp;
    bit<1>  cfi;
    bit<12> vid;
    bit<16> etherType;
}

header ipv4_t {
    bit<4>  version;
    bit<4>  ihl;
    bit<8>  diffserv;
    bit<16> totalLen;
    bit<16> identification;
    bit<3>  flags;
    bit<13> fragOffset;
    bit<8>  ttl;
    bit<8>  protocol;
    bit<16> hdrChecksum;
    bit<32> srcAddr;
    bit<32> dstAddr;
}

header ipv6_t {
    bit<4>   version;
    bit<8>   trafficClass;
    bit<20>  flowLabel;
    bit<16>  payloadLen;
    bit<8>   nextHdr;
    bit<8>   hopLimit;
    bit<128> srcAddr;
    bit<128> dstAddr;
}

header icmp_t   { bit<8> type_; bit<8> code; bit<16> hdrChecksum; }
header icmpv6_t { bit<8> type_; bit<8> code; bit<16> hdrChecksum; }

header tcp_t {
    bit<16> srcPort;
    bit<16> dstPort;
    bit<32> seqNo;
    bit<32> ackNo;
    bit<4>  dataOffset;
    bit<4>  res;
    bit<8>  flags;
    bit<16> window;
    bit<16> checksum;
    bit<16> urgentPtr;
}

header udp_t { bit<16> srcPort; bit<16> dstPort; bit<16> length_; bit<16> checksum; }

header gre_t {
    bit<1> C; bit<1> R; bit<1> K; bit<1> S; bit<1> s;
    bit<3> recurse;
    bit<5> flags;
    bit<3> ver;
    bit<16> proto;
}

header nvgre_t { bit<24> tni; bit<8> reserved; }

header vxlan_t { bit<8> flags; bit<24> rsvd; bit<24> vni; bit<8> rsvd2; }

header nsh_t {
    bit<1>  oam;
    bit<1>  context;
    bit<6>  flags;
    bit<8>  reserved;
    bit<16> protoType;
    bit<24> spath;
    bit<8>  sindex;
}

header nsh_context_t {
    bit<32> network_platform;
    bit<32> network_shared;
    bit<32> service_platform;
    bit<32> service_shared;
}

header genv_t {
    bit<2>  ver;
    bit<6>  optLen;
    bit<1>  oam;
    bit<1>  critical;
    bit<6>  reserved;
    bit<16> protoType;
    bit<24> vni;
    bit<8>  reserved2;
}

header arp_rarp_t {
    bit<16> hwType;
    bit<16> protoType;
    bit<8>  hwAddrLen;
    bit<8>  protoAddrLen;
    bit<16> opcode;
}

header arp_rarp_ipv4_t {
    bit<48> srcHwAddr;
    bit<32> srcProtoAddr;
    bit<48> dstHwAddr;
    bit<32> dstProtoAddr;
}

// ======================= HEADER STACK =======================

struct headers_t {
    ethernet_t ethernet;
    snap_header_t snap;
    cpu_header_t cpu;
    vlan_tag_t vlan;
    ipv4_t ipv4;
    ipv6_t ipv6;
    icmp_t icmp;
    icmpv6_t icmpv6;
    tcp_t tcp;
    udp_t udp;
    gre_t gre;
    nvgre_t nvgre;
    vxlan_t vxlan;
    nsh_t nsh;
    nsh_context_t nsh_ctx;
    genv_t genv;
    arp_rarp_t arp;
    arp_rarp_ipv4_t arp_ipv4;
    ethernet_t inner_ethernet;
    ipv4_t inner_ipv4;
    ipv6_t inner_ipv6;
    icmp_t inner_icmp;
    icmpv6_t inner_icmpv6;
    tcp_t inner_tcp;
    udp_t inner_udp;
}

// ======================= PARSER =======================

parser Parser(packet_in packet, out headers_t hdr) {

    state start {
        packet.extract(hdr.ethernet);
        transition select(hdr.ethernet.etherType) {
            16w0x9000 : parse_cpu;
            16w0x8100 : parse_vlan;
            16w0x0800 : parse_ipv4;
            16w0x86dd : parse_ipv6;
            16w0x0806 : parse_arp;
            16w0x894f : parse_nsh;
            default   : accept;
        }
    }

    state parse_cpu {
        packet.extract(hdr.cpu);
        transition select(hdr.cpu.etherType) {
            16w0x8100 : parse_vlan;
            16w0x0800 : parse_ipv4;
            16w0x86dd : parse_ipv6;
            16w0x0806 : parse_arp;
            16w0x894f : parse_nsh;
            default   : accept;
        }
    }

    state parse_vlan {
        packet.extract(hdr.vlan);
        transition select(hdr.vlan.etherType) {
            16w0x8100 : parse_vlan;
            16w0x0800 : parse_ipv4;
            16w0x86dd : parse_ipv6;
            16w0x0806 : parse_arp;
            default   : accept;
        }
    }

    state parse_ipv4 {
        packet.extract(hdr.ipv4);
        transition select(hdr.ipv4.protocol) {
            8w1  : parse_icmp;
            8w6  : parse_tcp;
            8w17 : parse_udp;
            8w47 : parse_gre;
            default : accept;
        }
    }

    state parse_ipv6 {
        packet.extract(hdr.ipv6);
        transition select(hdr.ipv6.nextHdr) {
            8w58 : parse_icmpv6;
            8w6  : parse_tcp;
            8w17 : parse_udp;
            8w47 : parse_gre;
            default : accept;
        }
    }

    state parse_icmp   { packet.extract(hdr.icmp);   transition accept; }
    state parse_icmpv6 { packet.extract(hdr.icmpv6); transition accept; }
    state parse_tcp    { packet.extract(hdr.tcp);    transition accept; }
    state parse_udp    { packet.extract(hdr.udp);    transition accept; }

    state parse_gre {
        packet.extract(hdr.gre);
        transition select(hdr.gre.proto) {
            16w0x6558 : parse_inner_ethernet;
            16w0x894f : parse_nsh;
            default   : accept;
        }
    }

    state parse_nsh {
        packet.extract(hdr.nsh);
        packet.extract(hdr.nsh_ctx);
        transition select(hdr.nsh.protoType) {
            16w0x0800 : parse_inner_ipv4;
            16w0x86dd : parse_inner_ipv6;
            16w0x6558 : parse_inner_ethernet;
            default   : accept;
        }
    }

    state parse_arp {
        packet.extract(hdr.arp);
        transition select(hdr.arp.protoType) {
            16w0x0800 : parse_arp_ipv4;
            default   : accept;
        }
    }

    state parse_arp_ipv4 {
        packet.extract(hdr.arp_ipv4);
        transition accept;
    }

    state parse_inner_ethernet {
        packet.extract(hdr.inner_ethernet);
        transition select(hdr.inner_ethernet.etherType) {
            16w0x0800 : parse_inner_ipv4;
            16w0x86dd : parse_inner_ipv6;
            default   : accept;
        }
    }

    state parse_inner_ipv4 {
        packet.extract(hdr.inner_ipv4);
        transition accept;
    }

    state parse_inner_ipv6 {
        packet.extract(hdr.inner_ipv6);
        transition accept;
    }
}

// ======================= FRAMEWORK =======================

parser Parser_t(packet_in packet, out headers_t hdr);
package Package(Parser_t p);
Package(Parser()) main;
