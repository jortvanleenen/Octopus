/* -*- P4_16 -*- */

#include <core.p4>

// ======================= CONSTANTS =======================

const bit<16> ETHERTYPE_IPV4      = 16w0x0800;
const bit<4>  IPV4_HEADER_LEN    = 4w5;
const bit<8>  IPV4_OPTION_SS     = 8w31;
const bit<8>  IPV4_OPTION_SS_CPU = 8w30;

// ======================= HEADERS =======================

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

header ipv4_option_t {
    bit<8> option;
    bit<8> length;
    bit<16> data;
}

header snapshot_header_t {
    bit<32> snapshot_id;
}

header tocpu_notif_t {
    bit<32> reason;
}

// ======================= HEADER STRUCT =======================

struct headers_t {
    ethernet_t ethernet;
    ipv4_t ipv4;
    ipv4_option_t ipv4_option;
    snapshot_header_t snapshot;
    tocpu_notif_t tocpu;
}

// ======================= PARSER =======================

parser Parser(packet_in packet, out headers_t hdr) {

    state start {
        packet.extract(hdr.ethernet);
        transition select(hdr.ethernet.etherType) {
            ETHERTYPE_IPV4 : parse_ipv4;
            default : accept;
        }
    }

    state parse_ipv4 {
        packet.extract(hdr.ipv4);
        transition select(hdr.ipv4.ihl) {
            IPV4_HEADER_LEN : accept;
            default : parse_ipv4_option;
        }
    }

    state parse_ipv4_option {
        packet.extract(hdr.ipv4_option);
        transition select(hdr.ipv4_option.option) {
            IPV4_OPTION_SS     : parse_snapshot;
            IPV4_OPTION_SS_CPU : parse_snapshot;
            default : accept;
        }
    }

    state parse_snapshot {
        packet.extract(hdr.snapshot);
        transition accept;
    }

    state parse_tocpu {
        packet.extract(hdr.tocpu);
        transition accept;
    }
}

// ======================= FRAMEWORK =======================

parser Parser_t(packet_in packet, out headers_t hdr);
package Package(Parser_t p);
Package(Parser()) main;
