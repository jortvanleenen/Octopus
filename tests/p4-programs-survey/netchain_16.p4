// HEADER START
#include <core.p4>
// HEADER END

struct location_t {
    bit<16> index;
}

struct my_md_t {
    bit<32> ipaddress;
    bit<16> role;
    bit<16> failed;
}

struct reply_addr_t {
    bit<32> ipv4_srcAddr;
    bit<32> ipv4_dstAddr;
}

struct sequence_md_t {
    bit<16> seq;
    bit<16> tmp;
}

header ethernet_t {
    bit<48> dstAddr;
    bit<48> srcAddr;
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

header nc_hdr_t {
    bit<8>   op;
    bit<8>   sc;
    bit<16>  seq;
    bit<128> key;
    bit<128> value;
    bit<16>  vgroup;
}

header tcp_t {
    bit<16> srcPort;
    bit<16> dstPort;
    bit<32> seqNo;
    bit<32> ackNo;
    bit<4>  dataOffset;
    bit<3>  res;
    bit<3>  ecn;
    bit<6>  ctrl;
    bit<16> window;
    bit<16> checksum;
    bit<16> urgentPtr;
}

header udp_t {
    bit<16> srcPort;
    bit<16> dstPort;
    bit<16> len;
    bit<16> checksum;
}

header overlay_t {
    bit<32> swip;
}

struct headers {
    @name(".ethernet") 
    ethernet_t    ethernet;
    @name(".ipv4") 
    ipv4_t        ipv4;
    @name(".nc_hdr") 
    nc_hdr_t      nc_hdr;
    @name(".tcp") 
    tcp_t         tcp;
    @name(".udp") 
    udp_t         udp;
    @name(".overlay") 
    overlay_t overlay;
}

parser Parser(packet_in packet, out headers hdr) {
    @name(".start") state start {
        packet.extract(hdr.ethernet);
        transition select(hdr.ethernet.etherType) {
            16w0x800: parse_ipv4;
            default: accept;
        }
    }
    @name(".parse_ipv4") state parse_ipv4 {
        packet.extract(hdr.ipv4);
        transition select(hdr.ipv4.protocol) {
            8w6: parse_tcp;
            8w17: parse_udp;
            default: accept;
        }
    }
    @name(".parse_nc_hdr") state parse_nc_hdr {
        packet.extract(hdr.nc_hdr);
        transition select(hdr.nc_hdr.op) {
            8w10: accept;
            8w12: accept;
            default: accept;
        }
    }
    @name(".parse_overlay") state parse_overlay {
        packet.extract(hdr.overlay);
        transition select(hdr.overlay.swip) {
            32w0: parse_nc_hdr;
            default: parse_overlay;
        }
    }
    @name(".parse_tcp") state parse_tcp {
        packet.extract(hdr.tcp);
        transition accept;
    }
    @name(".parse_udp") state parse_udp {
        packet.extract(hdr.udp);
        transition select(hdr.udp.dstPort) {
            16w8888: parse_overlay;
            16w8889: parse_overlay;
            default: accept;
        }
    }
}

// FOOTER START
parser Parser_t(packet_in packet, out headers hdr);
package Package(Parser_t p);

Package(Parser()) main;
// FOOTER END
