// HEADER START
#include <core.p4>
// HEADER END

header ethernet_t {
    bit<48> dstAddr;
    bit<48> srcAddr;
    bit<16> etherType;
}
header ptp_t {
    bit<4>  transportSpecific;
    bit<4>  messageType;
    bit<4>  reserved;
    bit<4>  versionPTP;
    bit<16> messageLength;
    bit<8>  domainNumber;
    bit<8>  reserved2;
    bit<16> flags;
    bit<64> correction;
    bit<32> reserved3;
    bit<80> sourcePortIdentity;
    bit<16> sequenceId;
    bit<8>  PTPcontrol;
    bit<8>  logMessagePeriod;
    bit<80> originTimestamp;
}
header header_0_t {
        bit<16> field_0;
        bit<16> field_1;
        bit<16> field_2;
        bit<16> field_3;

}
header header_1_t {
        bit<16> field_0;
        bit<16> field_1;
        bit<16> field_2;
        bit<16> field_3;

}
header header_2_t {
        bit<16> field_0;
        bit<16> field_1;
        bit<16> field_2;
        bit<16> field_3;

}
header header_3_t {
        bit<16> field_0;
        bit<16> field_1;
        bit<16> field_2;
        bit<16> field_3;

}
struct headers{
        ethernet_t ethernet;
        ptp_t    ptp;
        header_0_t header_0;
        header_1_t header_1;
        header_2_t header_2;
        header_3_t header_3;

}
parser Parser(packet_in packet, out headers hdr) {

    state start {
        transition parse_ethernet;
    }
    state parse_ethernet {
        packet.extract(hdr.ethernet);
        transition select(hdr.ethernet.etherType) {
                16w0x88f7: parse_ptp;
                default : accept;

        }
    }
    state parse_ptp {
        packet.extract(hdr.ptp);
        transition select(hdr.ptp.reserved2) {
                8w1     : parse_header_0;
                default : accept;

        }
    }
    state parse_header_0 {
        packet.extract(hdr.header_0);
        transition select(hdr.header_0.field_0) {
                16w0    : accept;
                default : parse_header_1;

        }
    }
    state parse_header_1 {
        packet.extract(hdr.header_1);
        transition select(hdr.header_1.field_0) {
                16w0    : accept;
                default : parse_header_2;

        }
    }
    state parse_header_2 {
        packet.extract(hdr.header_2);
        transition select(hdr.header_2.field_0) {
                16w0    : accept;
                default : parse_header_3;

        }
    }
    state parse_header_3 {
        packet.extract(hdr.header_3);
        transition select(hdr.header_3.field_0) {
                default : accept;

        }
    }


}

// FOOTER START
parser Parser_t(packet_in packet, out headers hdr);
package Package(Parser_t p);

Package(Parser()) main;
// FOOTER END
