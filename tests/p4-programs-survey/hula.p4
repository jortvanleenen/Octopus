// HEADER START
#include <core.p4>
// HEADER END

#define MAX_HOPS  9
#define TOR_NUM   32
#define TOR_NUM_1 33

/*************************************************************************
*********************** H E A D E R S  ***********************************
*************************************************************************/

typedef bit<9>  egressSpec_t;
typedef bit<48> macAddr_t;
typedef bit<32> ip4Addr_t;
typedef bit<15> qdepth_t;
typedef bit<32> digest_t;

header ethernet_t {
    macAddr_t dstAddr;
    macAddr_t srcAddr;
    bit<16>   etherType;
}

header srcRoute_t {
    bit<1>    bos;
    bit<15>   port;
}

header hula_t {
    /* 0 is forward path, 1 is the backward path */
    bit<1>   dir;
    /* max qdepth seen so far in the forward path */
    qdepth_t qdepth;
    /* digest of the source routing list to uniquely identify each path */
    digest_t digest;
}

header ipv4_t {
    bit<4>    version;
    bit<4>    ihl;
    bit<8>    diffserv;
    bit<16>   totalLen;
    bit<16>   identification;
    bit<3>    flags;
    bit<13>   fragOffset;
    bit<8>    ttl;
    bit<8>    protocol;
    bit<16>   hdrChecksum;
    ip4Addr_t srcAddr;
    ip4Addr_t dstAddr;
}

header udp_t {
    bit<16> srcPort;
    bit<16> dstPort;
    bit<16> length_;
    bit<16> checksum;
}

struct metadata {
    /* At destination ToR, this is the index of register 
       that saves qdepth for the best path from each source ToR */
    bit<32> index;
}

struct headers {
    ethernet_t              ethernet;
    srcRoute_t              srcRoute;
    ipv4_t                  ipv4;
    udp_t                   udp;
    hula_t                  hula;
}

/*************************************************************************
*********************** P A R S E R  ***********************************
*************************************************************************/

parser Parser(packet_in packet,
                out headers hdr) {

    state start {
        transition parse_ethernet;
    }

    state parse_ethernet {
        packet.extract(hdr.ethernet);
        transition select(hdr.ethernet.etherType) {
            0x2345 : parse_hula;
            0x800 : parse_ipv4;
            default   : accept;
        }
    }

    state parse_hula {
        packet.extract(hdr.hula);
        transition parse_srcRouting;
    }

    state parse_srcRouting {
        packet.extract(hdr.srcRoute);
        transition select(hdr.srcRoute.bos) {
            1       : parse_ipv4;
            default : parse_srcRouting;
        }
    }

    state parse_ipv4 {
        packet.extract(hdr.ipv4);
        transition select(hdr.ipv4.protocol) {
            8w17: parse_udp;
            default: accept;
        }
    }

    state parse_udp {
        packet.extract(hdr.udp);
        transition accept;
    }

}

// FOOTER START
parser Parser_t(packet_in packet, out headers hdr);
package Package(Parser_t p);

Package(Parser()) main;
// FOOTER END
