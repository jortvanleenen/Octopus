// HEADER START
#include <core.p4>
// HEADER END

header scratch8_t  { bit<8> data; }
header scratch16_t { bit<16> data; }
header scratch24_t { bit<24> data; }
header scratch32_t { bit<32> data; }
header scratch40_t { bit<40> data; }

header t0_t { bit<8> data; }
header l0_t { bit<8> data; }
header v0_t { bit<48> data; }

header t1_t { bit<8> data; }
header l1_t { bit<8> data; }
header v1_t { bit<48> data; }

header t2_t { bit<8> data; }
header l2_t { bit<8> data; }
header v2_t { bit<48> data; }

struct headers_t {
    t0_t t0;
    l0_t l0;
    v0_t v0;
    t1_t t1;
    l1_t l1;
    v1_t v1;
    t2_t t2;
    l2_t l2;
    v2_t v2;

    scratch8_t scratch8;
    scratch16_t scratch16;
    scratch24_t scratch24;
    scratch32_t scratch32;
    scratch40_t scratch40;
}

parser Parser(packet_in pkt, out headers_t hdr) {
    state start {
        pkt.extract(hdr.t0);
        pkt.extract(hdr.l0);
        transition select(hdr.t0.data, hdr.l0.data) {
            (0x00, 0x00): accept;
            (0x01, 0x00): accept;
            (_, 0x01): parse_01;
            (_, 0x02): parse_02;
            (_, 0x03): parse_03;
            (_, 0x04): parse_04;
            (_, 0x05): parse_05;
            (_, 0x06): parse_06;
            default: reject;
        }
    }

    state parse_01 {
        pkt.extract(hdr.scratch8);
        hdr.v0.data = hdr.scratch8.data ++ hdr.v0.data[47:8];
        transition parse_1;
    }

    state parse_02 {
        pkt.extract(hdr.scratch16);
        hdr.v0.data = hdr.scratch16.data ++ hdr.v0.data[47:16];
        transition parse_1;
    }

    state parse_03 {
        pkt.extract(hdr.scratch24);
        hdr.v0.data = hdr.scratch24.data ++ hdr.v0.data[47:24];
        transition parse_1;
    }

    state parse_04 {
        pkt.extract(hdr.scratch32);
        hdr.v0.data = hdr.scratch32.data ++ hdr.v0.data[47:32];
        transition parse_1;
    }

    state parse_05 {
        pkt.extract(hdr.scratch40);
        hdr.v0.data = hdr.scratch40.data ++ hdr.v0.data[47:40];
        transition parse_1;
    }

    state parse_06 {
        pkt.extract(hdr.v0);
        transition parse_1;
    }

    state parse_1 {
        pkt.extract(hdr.t1);
        pkt.extract(hdr.l1);
        transition select(hdr.t1.data, hdr.l1.data) {
            (0x00, 0x00): accept;
            (0x01, 0x00): accept;
            (_, 0x01): parse_11;
            (_, 0x02): parse_12;
            (_, 0x03): parse_13;
            (_, 0x04): parse_14;
            (_, 0x05): parse_15;
            (_, 0x06): parse_16;
            default: reject;
        }
    }

    state parse_11 {
        pkt.extract(hdr.scratch8);
        hdr.v1.data = hdr.scratch8.data ++ hdr.v1.data[47:8];
        transition parse_2;
    }

    state parse_12 {
        pkt.extract(hdr.scratch16);
        hdr.v1.data = hdr.scratch16.data ++ hdr.v1.data[47:16];
        transition parse_2;
    }

    state parse_13 {
        pkt.extract(hdr.scratch24);
        hdr.v1.data = hdr.scratch24.data ++ hdr.v1.data[47:24];
        transition parse_2;
    }

    state parse_14 {
        pkt.extract(hdr.scratch32);
        hdr.v1.data = hdr.scratch32.data ++ hdr.v1.data[47:32];
        transition parse_2;
    }

    state parse_15 {
        pkt.extract(hdr.scratch40);
        hdr.v1.data = hdr.scratch40.data ++ hdr.v1.data[47:40];
        transition parse_2;
    }

    state parse_16 {
        pkt.extract(hdr.v1);
        transition parse_2;
    }

    state parse_2 {
        pkt.extract(hdr.t2);
        pkt.extract(hdr.l2);
        transition select(hdr.t2.data, hdr.l2.data) {
            (0x00, 0x00): accept;
            (0x01, 0x00): accept;
            (_, 0x01): parse_21;
            (_, 0x02): parse_22;
            (_, 0x03): parse_23;
            (_, 0x04): parse_24;
            (_, 0x05): parse_25;
            (_, 0x06): parse_26;
            default: reject;
        }
    }

    state parse_21 {
        pkt.extract(hdr.scratch8);
        hdr.v2.data = hdr.scratch8.data ++ hdr.v2.data[47:8];
        transition accept;
    }

    state parse_22 {
        pkt.extract(hdr.scratch16);
        hdr.v2.data = hdr.scratch16.data ++ hdr.v2.data[47:16];
        transition accept;
    }

    state parse_23 {
        pkt.extract(hdr.scratch24);
        hdr.v2.data = hdr.scratch24.data ++ hdr.v2.data[47:24];
        transition accept;
    }

    state parse_24 {
        pkt.extract(hdr.scratch32);
        hdr.v2.data = hdr.scratch32.data ++ hdr.v2.data[47:32];
        transition accept;
    }

    state parse_25 {
        pkt.extract(hdr.scratch40);
        hdr.v2.data = hdr.scratch40.data ++ hdr.v2.data[47:40];
        transition accept;
    }

    state parse_26 {
        pkt.extract(hdr.v2);
        transition accept;
    }
}

// FOOTER START
parser Parser_t(packet_in pkt, out headers_t hdr);
package Package(Parser_t p);

Package(Parser()) main;
// FOOTER END
