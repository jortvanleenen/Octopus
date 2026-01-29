/* Copyright 2013-present Barefoot Networks, Inc.
 *
 * Licensed under the Apache License, Version 2.0
 */

// HEADER START
#include <core.p4>
// HEADER END

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

struct headers {
    ethernet_t ethernet;
    ipv4_t     ipv4;
}

parser Parser(packet_in packet, out headers hdr)
{
    state start {
        packet.extract(hdr.ethernet);
        packet.extract(hdr.ipv4);
        transition accept;
    }
}

// FOOTER START
parser Parser_t(packet_in packet, out headers hdr);

package Package(Parser_t p);

Package(Parser()) main;
// FOOTER END
