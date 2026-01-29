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
        bit<16> field_4;
        bit<16> field_5;
        bit<16> field_6;
        bit<16> field_7;
        bit<16> field_8;
        bit<16> field_9;
        bit<16> field_10;
        bit<16> field_11;
        bit<16> field_12;
        bit<16> field_13;
        bit<16> field_14;
        bit<16> field_15;
        bit<16> field_16;
        bit<16> field_17;
        bit<16> field_18;
        bit<16> field_19;
        bit<16> field_20;
        bit<16> field_21;
        bit<16> field_22;
        bit<16> field_23;
        bit<16> field_24;
        bit<16> field_25;
        bit<16> field_26;
        bit<16> field_27;
        bit<16> field_28;
        bit<16> field_29;
        bit<16> field_30;
        bit<16> field_31;
        bit<16> field_32;
        bit<16> field_33;
        bit<16> field_34;
        bit<16> field_35;
        bit<16> field_36;
        bit<16> field_37;
        bit<16> field_38;
        bit<16> field_39;
        bit<16> field_40;
        bit<16> field_41;
        bit<16> field_42;
        bit<16> field_43;
        bit<16> field_44;
        bit<16> field_45;
        bit<16> field_46;
        bit<16> field_47;
        bit<16> field_48;
        bit<16> field_49;
        bit<16> field_50;
        bit<16> field_51;
        bit<16> field_52;
        bit<16> field_53;
        bit<16> field_54;
        bit<16> field_55;
        bit<16> field_56;
        bit<16> field_57;
        bit<16> field_58;
        bit<16> field_59;
        bit<16> field_60;
        bit<16> field_61;
        bit<16> field_62;
        bit<16> field_63;

}
struct headers{
        ethernet_t ethernet;
        ptp_t    ptp;
        header_0_t header_0;

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
                default : accept;

        }
    }


}

// FOOTER START
parser Parser_t(packet_in packet, out headers hdr);
package Package(Parser_t p);

Package(Parser()) main;
// FOOTER END
