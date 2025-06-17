// HEADER START
#include <core.p4>
// HEADER END

header buf_16_t   { bit<16> data; }
header buf_32_t   { bit<32> data; }
header buf_48_t   { bit<48> data; }
header buf_112_t  { bit<112> data; }
header buf_144_t  { bit<144> data; }
header buf_176_t  { bit<176> data; }
header buf_208_t  { bit<208> data; }
header buf_240_t  { bit<240> data; }
header buf_304_t  { bit<304> data; }
header buf_320_t  { bit<320> data; }

struct headers_t {
    buf_16_t b16;
    buf_32_t b32;
    buf_48_t b48;
    buf_112_t b112;
    buf_144_t b144;
    buf_176_t b176;
    buf_208_t b208;
    buf_240_t b240;
    buf_304_t b304;
    buf_320_t b320;
}

parser Parser(packet_in pkt, out headers_t hdr) {
  state start {
    pkt.extract(hdr.b112);
    transition select (
      hdr.b112.data[15:15], hdr.b112.data[14:14], hdr.b112.data[13:13], hdr.b112.data[12:12],
      hdr.b112.data[11:11], hdr.b112.data[10:10], hdr.b112.data[9:9], hdr.b112.data[8:8],
      hdr.b112.data[7:7], hdr.b112.data[6:6], hdr.b112.data[5:5], hdr.b112.data[4:4],
      hdr.b112.data[3:3], hdr.b112.data[2:2], hdr.b112.data[1:1], hdr.b112.data[0:0],
      hdr.b112.data[111:111], hdr.b112.data[110:110], hdr.b112.data[109:109], hdr.b112.data[108:108],
      hdr.b112.data[107:107], hdr.b112.data[106:106], hdr.b112.data[105:105], hdr.b112.data[104:104],
      hdr.b112.data[103:103], hdr.b112.data[102:102], hdr.b112.data[101:101], hdr.b112.data[100:100],
      hdr.b112.data[99:99], hdr.b112.data[98:98], hdr.b112.data[97:97], hdr.b112.data[96:96]
    ) {
        (
            _, _, _, _, _, _, _, _,
            _, _, _, _, _, _, _, _,
            0, 0, 0, 0, 1, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0
        ) : state_1;

        (
            _, _, _, _, _, _, _, _,
            _, _, _, _, _, _, _, _,
            1, 0, 0, 0, 0, 1, 1, 0,
            1, 1, 0, 1, 1, 1, 0, 1
        ) : state_0_suff_1;

        (
            _, _, _, _, _, _, _, _,
            _, _, _, _, _, _, _, _,
            1, 0, 0, 0, 1, 0, 0, 0,
            0, 1, 0, 0, 0, 1, 1, 1
        ) : state_0_suff_2;

        (
            _, _, _, _, _, _, _, _,
            _, _, _, _, _, _, _, _,
            1, 0, 0, 0, 1, 0, 0, 0,
            0, 1, 0, 0, 1, 0, 0, 0
        ) : state_0_suff_3;

        default: reject;
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
        transition select (
            hdr.b16.data[15:15], hdr.b16.data[14:14], hdr.b16.data[13:13], hdr.b16.data[12:12],
            hdr.b16.data[11:11], hdr.b16.data[10:10], hdr.b16.data[9:9], hdr.b16.data[8:8],
            hdr.b16.data[7:7], hdr.b16.data[6:6], hdr.b16.data[5:5], hdr.b16.data[4:4],
            hdr.b16.data[3:3], hdr.b16.data[2:2], hdr.b16.data[1:1], hdr.b16.data[0:0],
            hdr.b16.data[15:15], hdr.b16.data[14:14], hdr.b16.data[13:13], hdr.b16.data[12:12],
            hdr.b16.data[11:11], hdr.b16.data[10:10], hdr.b16.data[9:9], hdr.b16.data[8:8],
            hdr.b16.data[7:7], hdr.b16.data[6:6], hdr.b16.data[5:5], hdr.b16.data[4:4],
            hdr.b16.data[3:3], hdr.b16.data[2:2], hdr.b16.data[1:1], hdr.b16.data[0:0]
        ) {
            (
                _, _, _, _,
                0, 1, 0, 1,
                _, _, _, _, _, _, _, _,
                _, _, _, _, _, _, _, _,
                _, _, _, _, _, _, _, _
            ) : state_1_suff_0;

            (
                _, _, _, _,
                0, 1, 1, 0,
                _, _, _, _, _, _, _, _,
                _, _, _, _, _, _, _, _,
                _, _, _, _, _, _, _, _
            ) : state_1_suff_1;

            (
                _, _, _, _,
                0, 1, 1, 1,
                _, _, _, _, _, _, _, _,
                _, _, _, _, _, _, _, _,
                _, _, _, _, _, _, _, _
            ) : state_1_suff_2;

            (
                _, _, _, _,
                1, 0, 0, 0,
                _, _, _, _, _, _, _, _,
                _, _, _, _, _, _, _, _,
                _, _, _, _, _, _, _, _
            ) : state_1_suff_3;

            default: reject;
        }
    }

    state state_1_suff_0 {
        pkt.extract(hdr.b144);
        transition accept;
    }

    state state_1_suff_1 {
        pkt.extract(hdr.b176);
        transition accept;
    }

    state state_1_suff_2 {
        pkt.extract(hdr.b208);
        transition accept;
    }

    state state_1_suff_3 {
        pkt.extract(hdr.b240);
        transition accept;
    }

    state state_2 {
        pkt.extract(hdr.b16);
        transition select (
            hdr.b16.data[15:15], hdr.b16.data[14:14], hdr.b16.data[13:13], hdr.b16.data[12:12],
            hdr.b16.data[11:11], hdr.b16.data[10:10], hdr.b16.data[9:9], hdr.b16.data[8:8],
            hdr.b16.data[7:7], hdr.b16.data[6:6], hdr.b16.data[5:5], hdr.b16.data[4:4],
            hdr.b16.data[3:3], hdr.b16.data[2:2], hdr.b16.data[1:1], hdr.b16.data[0:0],
            hdr.b16.data[15:15], hdr.b16.data[14:14], hdr.b16.data[13:13], hdr.b16.data[12:12],
            hdr.b16.data[11:11], hdr.b16.data[10:10], hdr.b16.data[9:9], hdr.b16.data[8:8],
            hdr.b16.data[7:7], hdr.b16.data[6:6], hdr.b16.data[5:5], hdr.b16.data[4:4],
            hdr.b16.data[3:3], hdr.b16.data[2:2], hdr.b16.data[1:1], hdr.b16.data[0:0]
        ) {
            (
                _, _, _, _, _, _, _, _,
                _, _, _, _, _, _, _, _,
                _, _, _, _, _, _, _, _,
                _, _, _, _, _, _, _, _
            ) : state_2_suff_0;

            default: reject;
        }
    }

    state state_2_suff_0 {
        pkt.extract(hdr.b304);
        transition accept;
    }

    state state_4 {
        pkt.extract(hdr.b16);
        transition select (
            hdr.b16.data[15:12],
            hdr.b16.data[8:8]
        ) {
            (0x4, 1): state_1;
            (0x6, 1): state_2;
            (_, 0): state_4_body;
            default: reject;
        }
    }

    state state_4_body {
        pkt.extract(hdr.b32);
        transition select (
            hdr.b32.data[31:31], hdr.b32.data[30:30], hdr.b32.data[29:29], hdr.b32.data[28:28],
            hdr.b32.data[27:27], hdr.b32.data[26:26], hdr.b32.data[25:25], hdr.b32.data[24:24],
            hdr.b32.data[23:23], hdr.b32.data[22:22], hdr.b32.data[21:21], hdr.b32.data[20:20],
            hdr.b32.data[19:19], hdr.b32.data[18:18], hdr.b32.data[17:17], hdr.b32.data[16:16]
        ) {
            (
                _, _, _, _, _, _, _, 0,
                _, _, _, _, _, _, _, _
            ) : state_4_suff_0;

            default: reject;
        }
    }

    state state_4_suff_0 {
        pkt.extract(hdr.b16);
        transition state_4;
    }
}

// FOOTER START
parser Parser_t(packet_in pkt, out headers_t hdr);
package Package(Parser_t p);

Package(Parser()) main;
// FOOTER END
