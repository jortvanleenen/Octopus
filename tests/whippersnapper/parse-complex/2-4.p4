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

}
header header_0_0_t {
        bit<16> field_0;

}
header header_0_0_0_t {
        bit<16> field_0;

}
header header_0_0_1_t {
        bit<16> field_0;

}
header header_0_0_2_t {
        bit<16> field_0;

}
header header_0_0_3_t {
        bit<16> field_0;

}
header header_0_1_t {
        bit<16> field_0;

}
header header_0_1_0_t {
        bit<16> field_0;

}
header header_0_1_1_t {
        bit<16> field_0;

}
header header_0_1_2_t {
        bit<16> field_0;

}
header header_0_1_3_t {
        bit<16> field_0;

}
header header_0_2_t {
        bit<16> field_0;

}
header header_0_2_0_t {
        bit<16> field_0;

}
header header_0_2_1_t {
        bit<16> field_0;

}
header header_0_2_2_t {
        bit<16> field_0;

}
header header_0_2_3_t {
        bit<16> field_0;

}
header header_0_3_t {
        bit<16> field_0;

}
header header_0_3_0_t {
        bit<16> field_0;

}
header header_0_3_1_t {
        bit<16> field_0;

}
header header_0_3_2_t {
        bit<16> field_0;

}
header header_0_3_3_t {
        bit<16> field_0;

}
struct headers{
        ethernet_t ethernet;
        ptp_t    ptp;
        header_0_t header_0;
        header_0_0_t header_0_0;
        header_0_0_0_t header_0_0_0;
        header_0_0_1_t header_0_0_1;
        header_0_0_2_t header_0_0_2;
        header_0_0_3_t header_0_0_3;
        header_0_1_t header_0_1;
        header_0_1_0_t header_0_1_0;
        header_0_1_1_t header_0_1_1;
        header_0_1_2_t header_0_1_2;
        header_0_1_3_t header_0_1_3;
        header_0_2_t header_0_2;
        header_0_2_0_t header_0_2_0;
        header_0_2_1_t header_0_2_1;
        header_0_2_2_t header_0_2_2;
        header_0_2_3_t header_0_2_3;
        header_0_3_t header_0_3;
        header_0_3_0_t header_0_3_0;
        header_0_3_1_t header_0_3_1;
        header_0_3_2_t header_0_3_2;
        header_0_3_3_t header_0_3_3;

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
                16w1    : parse_header_0_0;
                16w2    : parse_header_0_1;
                16w3    : parse_header_0_2;
                16w4    : parse_header_0_3;
                default : accept;

        }
    }
    state parse_header_0_0 {
        packet.extract(hdr.header_0_0);
        transition select(hdr.header_0_0.field_0) {
                16w1    : parse_header_0_0_0;
                16w2    : parse_header_0_0_1;
                16w3    : parse_header_0_0_2;
                16w4    : parse_header_0_0_3;
                default : accept;

        }
    }
    state parse_header_0_0_0 {
        packet.extract(hdr.header_0_0_0);
        transition select(hdr.header_0_0_0.field_0) {
                default : accept;

        }
    }
    state parse_header_0_0_1 {
        packet.extract(hdr.header_0_0_1);
        transition select(hdr.header_0_0_1.field_0) {
                default : accept;

        }
    }
    state parse_header_0_0_2 {
        packet.extract(hdr.header_0_0_2);
        transition select(hdr.header_0_0_2.field_0) {
                default : accept;

        }
    }
    state parse_header_0_0_3 {
        packet.extract(hdr.header_0_0_3);
        transition select(hdr.header_0_0_3.field_0) {
                default : accept;

        }
    }
    state parse_header_0_1 {
        packet.extract(hdr.header_0_1);
        transition select(hdr.header_0_1.field_0) {
                16w1    : parse_header_0_1_0;
                16w2    : parse_header_0_1_1;
                16w3    : parse_header_0_1_2;
                16w4    : parse_header_0_1_3;
                default : accept;

        }
    }
    state parse_header_0_1_0 {
        packet.extract(hdr.header_0_1_0);
        transition select(hdr.header_0_1_0.field_0) {
                default : accept;

        }
    }
    state parse_header_0_1_1 {
        packet.extract(hdr.header_0_1_1);
        transition select(hdr.header_0_1_1.field_0) {
                default : accept;

        }
    }
    state parse_header_0_1_2 {
        packet.extract(hdr.header_0_1_2);
        transition select(hdr.header_0_1_2.field_0) {
                default : accept;

        }
    }
    state parse_header_0_1_3 {
        packet.extract(hdr.header_0_1_3);
        transition select(hdr.header_0_1_3.field_0) {
                default : accept;

        }
    }
    state parse_header_0_2 {
        packet.extract(hdr.header_0_2);
        transition select(hdr.header_0_2.field_0) {
                16w1    : parse_header_0_2_0;
                16w2    : parse_header_0_2_1;
                16w3    : parse_header_0_2_2;
                16w4    : parse_header_0_2_3;
                default : accept;

        }
    }
    state parse_header_0_2_0 {
        packet.extract(hdr.header_0_2_0);
        transition select(hdr.header_0_2_0.field_0) {
                default : accept;

        }
    }
    state parse_header_0_2_1 {
        packet.extract(hdr.header_0_2_1);
        transition select(hdr.header_0_2_1.field_0) {
                default : accept;

        }
    }
    state parse_header_0_2_2 {
        packet.extract(hdr.header_0_2_2);
        transition select(hdr.header_0_2_2.field_0) {
                default : accept;

        }
    }
    state parse_header_0_2_3 {
        packet.extract(hdr.header_0_2_3);
        transition select(hdr.header_0_2_3.field_0) {
                default : accept;

        }
    }
    state parse_header_0_3 {
        packet.extract(hdr.header_0_3);
        transition select(hdr.header_0_3.field_0) {
                16w1    : parse_header_0_3_0;
                16w2    : parse_header_0_3_1;
                16w3    : parse_header_0_3_2;
                16w4    : parse_header_0_3_3;
                default : accept;

        }
    }
    state parse_header_0_3_0 {
        packet.extract(hdr.header_0_3_0);
        transition select(hdr.header_0_3_0.field_0) {
                default : accept;

        }
    }
    state parse_header_0_3_1 {
        packet.extract(hdr.header_0_3_1);
        transition select(hdr.header_0_3_1.field_0) {
                default : accept;

        }
    }
    state parse_header_0_3_2 {
        packet.extract(hdr.header_0_3_2);
        transition select(hdr.header_0_3_2.field_0) {
                default : accept;

        }
    }
    state parse_header_0_3_3 {
        packet.extract(hdr.header_0_3_3);
        transition select(hdr.header_0_3_3.field_0) {
                default : accept;

        }
    }


}

// FOOTER START
parser Parser_t(packet_in packet, out headers hdr);
package Package(Parser_t p);

Package(Parser()) main;
// FOOTER END
