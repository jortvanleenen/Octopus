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

}
header header_1_t {
        bit<16> field_0;
        bit<16> field_1;

}
header header_2_t {
        bit<16> field_0;
        bit<16> field_1;

}
header header_3_t {
        bit<16> field_0;
        bit<16> field_1;

}
header header_4_t {
        bit<16> field_0;
        bit<16> field_1;

}
header header_5_t {
        bit<16> field_0;
        bit<16> field_1;

}
header header_6_t {
        bit<16> field_0;
        bit<16> field_1;

}
header header_7_t {
        bit<16> field_0;
        bit<16> field_1;

}
header header_8_t {
        bit<16> field_0;
        bit<16> field_1;

}
header header_9_t {
        bit<16> field_0;
        bit<16> field_1;

}
header header_10_t {
        bit<16> field_0;
        bit<16> field_1;

}
header header_11_t {
        bit<16> field_0;
        bit<16> field_1;

}
header header_12_t {
        bit<16> field_0;
        bit<16> field_1;

}
header header_13_t {
        bit<16> field_0;
        bit<16> field_1;

}
header header_14_t {
        bit<16> field_0;
        bit<16> field_1;

}
header header_15_t {
        bit<16> field_0;
        bit<16> field_1;

}
header header_16_t {
        bit<16> field_0;
        bit<16> field_1;

}
header header_17_t {
        bit<16> field_0;
        bit<16> field_1;

}
header header_18_t {
        bit<16> field_0;
        bit<16> field_1;

}
header header_19_t {
        bit<16> field_0;
        bit<16> field_1;

}
header header_20_t {
        bit<16> field_0;
        bit<16> field_1;

}
header header_21_t {
        bit<16> field_0;
        bit<16> field_1;

}
header header_22_t {
        bit<16> field_0;
        bit<16> field_1;

}
header header_23_t {
        bit<16> field_0;
        bit<16> field_1;

}
header header_24_t {
        bit<16> field_0;
        bit<16> field_1;

}
header header_25_t {
        bit<16> field_0;
        bit<16> field_1;

}
header header_26_t {
        bit<16> field_0;
        bit<16> field_1;

}
header header_27_t {
        bit<16> field_0;
        bit<16> field_1;

}
header header_28_t {
        bit<16> field_0;
        bit<16> field_1;

}
header header_29_t {
        bit<16> field_0;
        bit<16> field_1;

}
header header_30_t {
        bit<16> field_0;
        bit<16> field_1;

}
header header_31_t {
        bit<16> field_0;
        bit<16> field_1;

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
        header_16_t header_16;
        header_17_t header_17;
        header_18_t header_18;
        header_19_t header_19;
        header_20_t header_20;
        header_21_t header_21;
        header_22_t header_22;
        header_23_t header_23;
        header_24_t header_24;
        header_25_t header_25;
        header_26_t header_26;
        header_27_t header_27;
        header_28_t header_28;
        header_29_t header_29;
        header_30_t header_30;
        header_31_t header_31;

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
                16w0    : accept;
                default : parse_header_16;

        }
    }
    state parse_header_16 {
        packet.extract(hdr.header_16);
        transition select(hdr.header_16.field_0) {
                16w0    : accept;
                default : parse_header_17;

        }
    }
    state parse_header_17 {
        packet.extract(hdr.header_17);
        transition select(hdr.header_17.field_0) {
                16w0    : accept;
                default : parse_header_18;

        }
    }
    state parse_header_18 {
        packet.extract(hdr.header_18);
        transition select(hdr.header_18.field_0) {
                16w0    : accept;
                default : parse_header_19;

        }
    }
    state parse_header_19 {
        packet.extract(hdr.header_19);
        transition select(hdr.header_19.field_0) {
                16w0    : accept;
                default : parse_header_20;

        }
    }
    state parse_header_20 {
        packet.extract(hdr.header_20);
        transition select(hdr.header_20.field_0) {
                16w0    : accept;
                default : parse_header_21;

        }
    }
    state parse_header_21 {
        packet.extract(hdr.header_21);
        transition select(hdr.header_21.field_0) {
                16w0    : accept;
                default : parse_header_22;

        }
    }
    state parse_header_22 {
        packet.extract(hdr.header_22);
        transition select(hdr.header_22.field_0) {
                16w0    : accept;
                default : parse_header_23;

        }
    }
    state parse_header_23 {
        packet.extract(hdr.header_23);
        transition select(hdr.header_23.field_0) {
                16w0    : accept;
                default : parse_header_24;

        }
    }
    state parse_header_24 {
        packet.extract(hdr.header_24);
        transition select(hdr.header_24.field_0) {
                16w0    : accept;
                default : parse_header_25;

        }
    }
    state parse_header_25 {
        packet.extract(hdr.header_25);
        transition select(hdr.header_25.field_0) {
                16w0    : accept;
                default : parse_header_26;

        }
    }
    state parse_header_26 {
        packet.extract(hdr.header_26);
        transition select(hdr.header_26.field_0) {
                16w0    : accept;
                default : parse_header_27;

        }
    }
    state parse_header_27 {
        packet.extract(hdr.header_27);
        transition select(hdr.header_27.field_0) {
                16w0    : accept;
                default : parse_header_28;

        }
    }
    state parse_header_28 {
        packet.extract(hdr.header_28);
        transition select(hdr.header_28.field_0) {
                16w0    : accept;
                default : parse_header_29;

        }
    }
    state parse_header_29 {
        packet.extract(hdr.header_29);
        transition select(hdr.header_29.field_0) {
                16w0    : accept;
                default : parse_header_30;

        }
    }
    state parse_header_30 {
        packet.extract(hdr.header_30);
        transition select(hdr.header_30.field_0) {
                16w0    : accept;
                default : parse_header_31;

        }
    }
    state parse_header_31 {
        packet.extract(hdr.header_31);
        transition select(hdr.header_31.field_0) {
                default : accept;

        }
    }


}

// FOOTER START
parser Parser_t(packet_in packet, out headers hdr);
package Package(Parser_t p);

Package(Parser()) main;
// FOOTER END
