// HEADER START
#include <core.p4>
// HEADER END

header buf_16_t   { bit<16> data; }
header buf_32_t   { bit<32> data; }
header buf_64_t   { bit<64> data; }
header buf_112_t  { bit<112> data; }
header buf_128_t  { bit<128> data; }
header buf_144_t  { bit<144> data; }
header buf_176_t  { bit<176> data; }
header buf_208_t  { bit<208> data; }
header buf_240_t  { bit<240> data; }
header buf_304_t  { bit<304> data; }
header buf_320_t  { bit<320> data; }

struct headers_t {
    buf_16_t   b16;
    buf_32_t   b32;
    buf_64_t   b64;
    buf_112_t  b112;
    buf_128_t  b128;
    buf_144_t  b144;
    buf_176_t  b176;
    buf_208_t  b208;
    buf_240_t  b240;
    buf_304_t  b304;
    buf_320_t  b320;
}

parser Parser(packet_in pkt, out headers_t hdr) {
    state start {
        pkt.extract(hdr.b112);
        transition select(hdr.b112.data[111:96]) {
            (0x8020): state_3;
            (0x886d): state_0_suff_1;
            (0x8857): state_0_suff_2;
            (0x8868): state_0_suff_3;
            default: accept;
        }
    }

    state state_0_suff_1 {
        pkt.extract(hdr.b320);
        transition accept;
    }

    state state_0_suff_2 {
        pkt.extract(hdr.b16);
        transition state_4;
    }

    state state_0_suff_3 {
        pkt.extract(hdr.b16);
        transition state_4;
    }

    state state_1 {
        pkt.extract(hdr.b16);
        transition state_1_suff_0;
    }

    state state_1_suff_0 {
        pkt.extract(hdr.b128);
        transition accept;
    }

    state state_2 {
        pkt.extract(hdr.b16);
        transition state_2_suff_0;
    }

    state state_2_suff_0 {
        pkt.extract(hdr.b304);
        transition accept;
    }

    state state_3 {
        pkt.extract(hdr.b16);
        transition select(hdr.b16.data[7:4]) {
            (0x5): state_3_suff_0;
            (0x6): state_3_suff_1;
            (0x7): state_3_suff_2;
            (0x8): state_3_suff_3;
            default: reject;
        }
    }

    state state_3_suff_0 {
        pkt.extract(hdr.b144);
        transition accept;
    }

    state state_3_suff_1 {
        pkt.extract(hdr.b176);
        transition accept;
    }

    state state_3_suff_2 {
        pkt.extract(hdr.b208);
        transition accept;
    }

    state state_3_suff_3 {
        pkt.extract(hdr.b240);
        transition accept;
    }

    state state_4 {
        pkt.extract(hdr.b16);
        transition select(hdr.b16.data[7:7]) {
            (0b0): state_4_skip;
            (0b1): state_4_trailer;
            default: reject;
        }
    }

    state state_4_skip {
        pkt.extract(hdr.b32);
        transition select(hdr.b32.data[23:23]) {
            (0b1): state_4_trailer;
            default: reject;
        }
    }

    state state_4_trailer {
        pkt.extract(hdr.b16);
        transition select(hdr.b16.data[3:0], hdr.b16.data[7:4]) {
            (0x0,  _):     state_1_suff_0;
            (0x6,  _):     state_2_suff_0;
            (0x4, 0x5):    state_3_suff_0;
            (0x4, 0x6):    state_3_suff_1;
            (0x4, 0x7):    state_3_suff_2;
            (0x4, 0x8):    state_3_suff_3;
            default:       reject;
        }
    }
}

// FOOTER START
parser Parser_t(packet_in pkt, out headers_t hdr);
package Package(Parser_t p);

Package(Parser()) main;
// FOOTER END
