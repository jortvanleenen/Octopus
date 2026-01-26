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
header header_1_t {
        bit<16> field_0;

}
header header_2_t {
        bit<16> field_0;

}
header header_3_t {
        bit<16> field_0;

}
header header_4_t {
        bit<16> field_0;

}
header header_5_t {
        bit<16> field_0;

}
header header_6_t {
        bit<16> field_0;

}
header header_7_t {
        bit<16> field_0;

}
header header_8_t {
        bit<16> field_0;

}
header header_9_t {
        bit<16> field_0;

}
header header_10_t {
        bit<16> field_0;

}
header header_11_t {
        bit<16> field_0;

}
header header_12_t {
        bit<16> field_0;

}
header header_13_t {
        bit<16> field_0;

}
header header_14_t {
        bit<16> field_0;

}
header header_15_t {
        bit<16> field_0;

}
header header_16_t {
        bit<16> field_0;

}
header header_17_t {
        bit<16> field_0;

}
header header_18_t {
        bit<16> field_0;

}
header header_19_t {
        bit<16> field_0;

}
header header_20_t {
        bit<16> field_0;

}
header header_21_t {
        bit<16> field_0;

}
header header_22_t {
        bit<16> field_0;

}
header header_23_t {
        bit<16> field_0;

}
header header_24_t {
        bit<16> field_0;

}
header header_25_t {
        bit<16> field_0;

}
header header_26_t {
        bit<16> field_0;

}
header header_27_t {
        bit<16> field_0;

}
header header_28_t {
        bit<16> field_0;

}
header header_29_t {
        bit<16> field_0;

}
header header_30_t {
        bit<16> field_0;

}
header header_31_t {
        bit<16> field_0;

}
header header_32_t {
        bit<16> field_0;

}
header header_33_t {
        bit<16> field_0;

}
header header_34_t {
        bit<16> field_0;

}
header header_35_t {
        bit<16> field_0;

}
header header_36_t {
        bit<16> field_0;

}
header header_37_t {
        bit<16> field_0;

}
header header_38_t {
        bit<16> field_0;

}
header header_39_t {
        bit<16> field_0;

}
header header_40_t {
        bit<16> field_0;

}
header header_41_t {
        bit<16> field_0;

}
header header_42_t {
        bit<16> field_0;

}
header header_43_t {
        bit<16> field_0;

}
header header_44_t {
        bit<16> field_0;

}
header header_45_t {
        bit<16> field_0;

}
header header_46_t {
        bit<16> field_0;

}
header header_47_t {
        bit<16> field_0;

}
header header_48_t {
        bit<16> field_0;

}
header header_49_t {
        bit<16> field_0;

}
header header_50_t {
        bit<16> field_0;

}
header header_51_t {
        bit<16> field_0;

}
header header_52_t {
        bit<16> field_0;

}
header header_53_t {
        bit<16> field_0;

}
header header_54_t {
        bit<16> field_0;

}
header header_55_t {
        bit<16> field_0;

}
header header_56_t {
        bit<16> field_0;

}
header header_57_t {
        bit<16> field_0;

}
header header_58_t {
        bit<16> field_0;

}
header header_59_t {
        bit<16> field_0;

}
header header_60_t {
        bit<16> field_0;

}
header header_61_t {
        bit<16> field_0;

}
header header_62_t {
        bit<16> field_0;

}
header header_63_t {
        bit<16> field_0;

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
        header_32_t header_32;
        header_33_t header_33;
        header_34_t header_34;
        header_35_t header_35;
        header_36_t header_36;
        header_37_t header_37;
        header_38_t header_38;
        header_39_t header_39;
        header_40_t header_40;
        header_41_t header_41;
        header_42_t header_42;
        header_43_t header_43;
        header_44_t header_44;
        header_45_t header_45;
        header_46_t header_46;
        header_47_t header_47;
        header_48_t header_48;
        header_49_t header_49;
        header_50_t header_50;
        header_51_t header_51;
        header_52_t header_52;
        header_53_t header_53;
        header_54_t header_54;
        header_55_t header_55;
        header_56_t header_56;
        header_57_t header_57;
        header_58_t header_58;
        header_59_t header_59;
        header_60_t header_60;
        header_61_t header_61;
        header_62_t header_62;
        header_63_t header_63;

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
                16w0    : accept;
                default : parse_header_32;

        }
    }
    state parse_header_32 {
        packet.extract(hdr.header_32);
        transition select(hdr.header_32.field_0) {
                16w0    : accept;
                default : parse_header_33;

        }
    }
    state parse_header_33 {
        packet.extract(hdr.header_33);
        transition select(hdr.header_33.field_0) {
                16w0    : accept;
                default : parse_header_34;

        }
    }
    state parse_header_34 {
        packet.extract(hdr.header_34);
        transition select(hdr.header_34.field_0) {
                16w0    : accept;
                default : parse_header_35;

        }
    }
    state parse_header_35 {
        packet.extract(hdr.header_35);
        transition select(hdr.header_35.field_0) {
                16w0    : accept;
                default : parse_header_36;

        }
    }
    state parse_header_36 {
        packet.extract(hdr.header_36);
        transition select(hdr.header_36.field_0) {
                16w0    : accept;
                default : parse_header_37;

        }
    }
    state parse_header_37 {
        packet.extract(hdr.header_37);
        transition select(hdr.header_37.field_0) {
                16w0    : accept;
                default : parse_header_38;

        }
    }
    state parse_header_38 {
        packet.extract(hdr.header_38);
        transition select(hdr.header_38.field_0) {
                16w0    : accept;
                default : parse_header_39;

        }
    }
    state parse_header_39 {
        packet.extract(hdr.header_39);
        transition select(hdr.header_39.field_0) {
                16w0    : accept;
                default : parse_header_40;

        }
    }
    state parse_header_40 {
        packet.extract(hdr.header_40);
        transition select(hdr.header_40.field_0) {
                16w0    : accept;
                default : parse_header_41;

        }
    }
    state parse_header_41 {
        packet.extract(hdr.header_41);
        transition select(hdr.header_41.field_0) {
                16w0    : accept;
                default : parse_header_42;

        }
    }
    state parse_header_42 {
        packet.extract(hdr.header_42);
        transition select(hdr.header_42.field_0) {
                16w0    : accept;
                default : parse_header_43;

        }
    }
    state parse_header_43 {
        packet.extract(hdr.header_43);
        transition select(hdr.header_43.field_0) {
                16w0    : accept;
                default : parse_header_44;

        }
    }
    state parse_header_44 {
        packet.extract(hdr.header_44);
        transition select(hdr.header_44.field_0) {
                16w0    : accept;
                default : parse_header_45;

        }
    }
    state parse_header_45 {
        packet.extract(hdr.header_45);
        transition select(hdr.header_45.field_0) {
                16w0    : accept;
                default : parse_header_46;

        }
    }
    state parse_header_46 {
        packet.extract(hdr.header_46);
        transition select(hdr.header_46.field_0) {
                16w0    : accept;
                default : parse_header_47;

        }
    }
    state parse_header_47 {
        packet.extract(hdr.header_47);
        transition select(hdr.header_47.field_0) {
                16w0    : accept;
                default : parse_header_48;

        }
    }
    state parse_header_48 {
        packet.extract(hdr.header_48);
        transition select(hdr.header_48.field_0) {
                16w0    : accept;
                default : parse_header_49;

        }
    }
    state parse_header_49 {
        packet.extract(hdr.header_49);
        transition select(hdr.header_49.field_0) {
                16w0    : accept;
                default : parse_header_50;

        }
    }
    state parse_header_50 {
        packet.extract(hdr.header_50);
        transition select(hdr.header_50.field_0) {
                16w0    : accept;
                default : parse_header_51;

        }
    }
    state parse_header_51 {
        packet.extract(hdr.header_51);
        transition select(hdr.header_51.field_0) {
                16w0    : accept;
                default : parse_header_52;

        }
    }
    state parse_header_52 {
        packet.extract(hdr.header_52);
        transition select(hdr.header_52.field_0) {
                16w0    : accept;
                default : parse_header_53;

        }
    }
    state parse_header_53 {
        packet.extract(hdr.header_53);
        transition select(hdr.header_53.field_0) {
                16w0    : accept;
                default : parse_header_54;

        }
    }
    state parse_header_54 {
        packet.extract(hdr.header_54);
        transition select(hdr.header_54.field_0) {
                16w0    : accept;
                default : parse_header_55;

        }
    }
    state parse_header_55 {
        packet.extract(hdr.header_55);
        transition select(hdr.header_55.field_0) {
                16w0    : accept;
                default : parse_header_56;

        }
    }
    state parse_header_56 {
        packet.extract(hdr.header_56);
        transition select(hdr.header_56.field_0) {
                16w0    : accept;
                default : parse_header_57;

        }
    }
    state parse_header_57 {
        packet.extract(hdr.header_57);
        transition select(hdr.header_57.field_0) {
                16w0    : accept;
                default : parse_header_58;

        }
    }
    state parse_header_58 {
        packet.extract(hdr.header_58);
        transition select(hdr.header_58.field_0) {
                16w0    : accept;
                default : parse_header_59;

        }
    }
    state parse_header_59 {
        packet.extract(hdr.header_59);
        transition select(hdr.header_59.field_0) {
                16w0    : accept;
                default : parse_header_60;

        }
    }
    state parse_header_60 {
        packet.extract(hdr.header_60);
        transition select(hdr.header_60.field_0) {
                16w0    : accept;
                default : parse_header_61;

        }
    }
    state parse_header_61 {
        packet.extract(hdr.header_61);
        transition select(hdr.header_61.field_0) {
                16w0    : accept;
                default : parse_header_62;

        }
    }
    state parse_header_62 {
        packet.extract(hdr.header_62);
        transition select(hdr.header_62.field_0) {
                16w0    : accept;
                default : parse_header_63;

        }
    }
    state parse_header_63 {
        packet.extract(hdr.header_63);
        transition select(hdr.header_63.field_0) {
                default : accept;

        }
    }


}

// FOOTER START
parser Parser_t(packet_in packet, out headers hdr);
package Package(Parser_t p);

Package(Parser()) main;
// FOOTER END
