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
header header_4_t {
        bit<16> field_0;
        bit<16> field_1;
        bit<16> field_2;
        bit<16> field_3;

}
header header_5_t {
        bit<16> field_0;
        bit<16> field_1;
        bit<16> field_2;
        bit<16> field_3;

}
header header_6_t {
        bit<16> field_0;
        bit<16> field_1;
        bit<16> field_2;
        bit<16> field_3;

}
header header_7_t {
        bit<16> field_0;
        bit<16> field_1;
        bit<16> field_2;
        bit<16> field_3;

}
header header_8_t {
        bit<16> field_0;
        bit<16> field_1;
        bit<16> field_2;
        bit<16> field_3;

}
header header_9_t {
        bit<16> field_0;
        bit<16> field_1;
        bit<16> field_2;
        bit<16> field_3;

}
header header_10_t {
        bit<16> field_0;
        bit<16> field_1;
        bit<16> field_2;
        bit<16> field_3;

}
header header_11_t {
        bit<16> field_0;
        bit<16> field_1;
        bit<16> field_2;
        bit<16> field_3;

}
header header_12_t {
        bit<16> field_0;
        bit<16> field_1;
        bit<16> field_2;
        bit<16> field_3;

}
header header_13_t {
        bit<16> field_0;
        bit<16> field_1;
        bit<16> field_2;
        bit<16> field_3;

}
header header_14_t {
        bit<16> field_0;
        bit<16> field_1;
        bit<16> field_2;
        bit<16> field_3;

}
header header_15_t {
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
        header_4_t header_4;
        header_5_t header_5;
        header_6_t header_6;
        header_7_t header_7;
        header_8_t header_8;
        header_9_t header_9;
        header_10_t header_10;
        header_11_t header_11;
        header_12_t header_12;
        header_13_t header_13;
        header_14_t header_14;
        header_15_t header_15;

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
                16w0    : accept;
                default : parse_header_4;

        }
    }
    state parse_header_4 {
        packet.extract(hdr.header_4);
        transition select(hdr.header_4.field_0) {
                16w0    : accept;
                default : parse_header_5;

        }
    }
    state parse_header_5 {
        packet.extract(hdr.header_5);
        transition select(hdr.header_5.field_0) {
                16w0    : accept;
                default : parse_header_6;

        }
    }
    state parse_header_6 {
        packet.extract(hdr.header_6);
        transition select(hdr.header_6.field_0) {
                16w0    : accept;
                default : parse_header_7;

        }
    }
    state parse_header_7 {
        packet.extract(hdr.header_7);
        transition select(hdr.header_7.field_0) {
                16w0    : accept;
                default : parse_header_8;

        }
    }
    state parse_header_8 {
        packet.extract(hdr.header_8);
        transition select(hdr.header_8.field_0) {
                16w0    : accept;
                default : parse_header_9;

        }
    }
    state parse_header_9 {
        packet.extract(hdr.header_9);
        transition select(hdr.header_9.field_0) {
                16w0    : accept;
                default : parse_header_10;

        }
    }
    state parse_header_10 {
        packet.extract(hdr.header_10);
        transition select(hdr.header_10.field_0) {
                16w0    : accept;
                default : parse_header_11;

        }
    }
    state parse_header_11 {
        packet.extract(hdr.header_11);
        transition select(hdr.header_11.field_0) {
                16w0    : accept;
                default : parse_header_12;

        }
    }
    state parse_header_12 {
        packet.extract(hdr.header_12);
        transition select(hdr.header_12.field_0) {
                16w0    : accept;
                default : parse_header_13;

        }
    }
    state parse_header_13 {
        packet.extract(hdr.header_13);
        transition select(hdr.header_13.field_0) {
                16w0    : accept;
                default : parse_header_14;

        }
    }
    state parse_header_14 {
        packet.extract(hdr.header_14);
        transition select(hdr.header_14.field_0) {
                16w0    : accept;
                default : parse_header_15;

        }
    }
    state parse_header_15 {
        packet.extract(hdr.header_15);
        transition select(hdr.header_15.field_0) {
                default : accept;

        }
    }


}

// FOOTER START
parser Parser_t(packet_in packet, out headers hdr);
package Package(Parser_t p);

Package(Parser()) main;
// FOOTER END
