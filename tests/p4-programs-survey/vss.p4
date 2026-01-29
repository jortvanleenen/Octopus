// HEADER START
#include <core.p4>
// HEADER END

// This program processes packets composed of an Ethernet and
// an IPv4 header, performing forwarding based on the
// destination IP address

// standard Ethernet header
header Ethernet_h {
    bit<48> dstAddr;
    bit<48> srcAddr;
    bit<16>         etherType;
}

// IPv4 header without options
header Ipv4_h {
    bit<4>       version;
    bit<4>       ihl;
    bit<8>       diffserv;
    bit<16>      totalLen;
    bit<16>      identification;
    bit<3>       flags;
    bit<13>      fragOffset;
    bit<8>       ttl;
    bit<8>       protocol;
    bit<16>      hdrChecksum;
    bit<32>      srcAddr;
    bit<32>      dstAddr;
}

// Parser section

// List of all recognized headers
struct Parsed_packet {
    Ethernet_h ethernet;
    Ipv4_h     ip;
}

parser Parser(packet_in b, out Parsed_packet p) {
    state start {
        b.extract(p.ethernet);
        transition select(p.ethernet.etherType) {
            0x0800 : parse_ipv4;
            default: reject;
        }
    }

    state parse_ipv4 {
        b.extract(p.ip);
        transition accept;
    }
}

// FOOTER START
parser Parser_t(packet_in b, out Parsed_packet p);
package Package(Parser_t p);

Package(Parser()) main;
// FOOTER END