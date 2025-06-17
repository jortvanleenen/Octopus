// HEADER START
#include <core.p4>
// HEADER END

header buf_16_t   { bit<16> data; }
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
    buf_112_t buf112;
    buf_320_t buf320;
    buf_16_t buf16;
    buf_64_t buf64;
    buf_128_t buf128;
    buf_304_t buf304;
    buf_144_t buf144;
    buf_176_t buf176;
    buf_208_t buf208;
    buf_240_t buf240;
}


parser Parser(packet_in pkt, out headers_t hdr) {
    state start {
        pkt.extract(hdr.buf112);
        transition select (
            hdr.buf112.data[15:15], hdr.buf112.data[14:14], hdr.buf112.data[13:13], hdr.buf112.data[12:12],
            hdr.buf112.data[11:11], hdr.buf112.data[10:10], hdr.buf112.data[9:9],   hdr.buf112.data[8:8],
            hdr.buf112.data[7:7],   hdr.buf112.data[6:6],   hdr.buf112.data[5:5],   hdr.buf112.data[4:4],
            hdr.buf112.data[3:3],   hdr.buf112.data[2:2],   hdr.buf112.data[1:1],   hdr.buf112.data[0:0],
            hdr.buf112.data[111:111], hdr.buf112.data[110:110], hdr.buf112.data[109:109], hdr.buf112.data[108:108],
            hdr.buf112.data[107:107], hdr.buf112.data[106:106], hdr.buf112.data[105:105], hdr.buf112.data[104:104],
            hdr.buf112.data[103:103], hdr.buf112.data[102:102], hdr.buf112.data[101:101], hdr.buf112.data[100:100],
            hdr.buf112.data[99:99],   hdr.buf112.data[98:98],   hdr.buf112.data[97:97],   hdr.buf112.data[96:96],
            hdr.buf112.data[15:15], hdr.buf112.data[14:14], hdr.buf112.data[13:13], hdr.buf112.data[12:12],
            hdr.buf112.data[11:11], hdr.buf112.data[10:10], hdr.buf112.data[9:9],   hdr.buf112.data[8:8],
            hdr.buf112.data[7:7],   hdr.buf112.data[6:6],   hdr.buf112.data[5:5],   hdr.buf112.data[4:4],
            hdr.buf112.data[3:3],   hdr.buf112.data[2:2],   hdr.buf112.data[1:1],   hdr.buf112.data[0:0],
            hdr.buf112.data[15:15], hdr.buf112.data[14:14], hdr.buf112.data[13:13], hdr.buf112.data[12:12],
            hdr.buf112.data[11:11], hdr.buf112.data[10:10], hdr.buf112.data[9:9],   hdr.buf112.data[8:8],
            hdr.buf112.data[7:7],   hdr.buf112.data[6:6],   hdr.buf112.data[5:5],   hdr.buf112.data[4:4],
            hdr.buf112.data[3:3],   hdr.buf112.data[2:2],   hdr.buf112.data[1:1],   hdr.buf112.data[0:0]
        ) {
            (
                _, _, _, _, _, _, _, _,
                _, _, _, _, _, _, _, _,
                0, 0, 0, 0, 1, 0, 0, 0,
                0, 0, 0, 0, 0, 0, 0, 0,
                _, _, _, _, _, _, _, _,
                _, _, _, _, _, _, _, _,
                _, _, _, _, _, _, _, _,
                _, _, _, _, _, _, _, _
            ) : accept;

            (
                _, _, _, _, _, _, _, _,
                _, _, _, _, _, _, _, _,
                1, 0, 0, 0, 0, 1, 1, 0,
                1, 1, 0, 1, 1, 1, 0, 1,
                _, _, _, _, _, _, _, _,
                _, _, _, _, _, _, _, _,
                _, _, _, _, _, _, _, _,
                _, _, _, _, _, _, _, _
            ) : State_0_suff_1;

            (
                _, _, _, _, _, _, _, _,
                _, _, _, _, _, _, _, _,
                1, 0, 0, 0, 1, 0, 0, 0,
                0, 1, 0, 0, 0, 1, 1, 1,
                _, _, _, _, _, _, _, _,
                _, _, _, _, _, _, _, _,
                _, _, _, _, _, _, _, _,
                _, _, _, _, _, _, _, _
            ) : State_0_suff_2;

            (
                _, _, _, _, _, _, _, _,
                _, _, _, _, _, _, _, _,
                1, 0, 0, 0, 1, 0, 0, 0,
                0, 1, 0, 0, 1, 0, 0, 0,
                _, _, _, _, _, _, _, _,
                _, _, _, _, _, _, _, _,
                _, _, _, _, _, _, _, _,
                _, _, _, _, _, _, _, _
            ) : State_0_suff_3;

            (
                _, _, _, _, _, _, _, _,
                _, _, _, _, _, _, _, _,
                _, _, _, _, _, _, _, _,
                _, _, _, _, _, _, _, _,
                _, _, _, _, _, _, _, _,
                _, _, _, _, _, _, _, _,
                _, _, _, _, _, _, _, _,
                _, _, _, _, _, _, _, _
            ) : accept;

            default: reject;
        }
    }

    state State_0_suff_1 {
        pkt.extract(hdr.buf320);
        transition accept;
    }

    state State_0_suff_2 {
        pkt.extract(hdr.buf16);
        transition State_2;
    }

    state State_0_suff_3 {
        pkt.extract(hdr.buf16);
        transition State_3;
    }

    state State_1 {
        pkt.extract(hdr.buf16);
        transition select (
            hdr.buf16.data[15:15], hdr.buf16.data[14:14], hdr.buf16.data[13:13], hdr.buf16.data[12:12],
            hdr.buf16.data[11:11], hdr.buf16.data[10:10], hdr.buf16.data[9:9],   hdr.buf16.data[8:8],
            hdr.buf16.data[7:7],   hdr.buf16.data[6:6],   hdr.buf16.data[5:5],   hdr.buf16.data[4:4],
            hdr.buf16.data[3:3],   hdr.buf16.data[2:2],   hdr.buf16.data[1:1],   hdr.buf16.data[0:0],
            hdr.buf16.data[15:15], hdr.buf16.data[14:14], hdr.buf16.data[13:13], hdr.buf16.data[12:12],
            hdr.buf16.data[11:11], hdr.buf16.data[10:10], hdr.buf16.data[9:9],   hdr.buf16.data[8:8],
            hdr.buf16.data[7:7],   hdr.buf16.data[6:6],   hdr.buf16.data[5:5],   hdr.buf16.data[4:4],
            hdr.buf16.data[3:3],   hdr.buf16.data[2:2],   hdr.buf16.data[1:1],   hdr.buf16.data[0:0],
            hdr.buf16.data[15:15], hdr.buf16.data[14:14], hdr.buf16.data[13:13], hdr.buf16.data[12:12],
            hdr.buf16.data[11:11], hdr.buf16.data[10:10], hdr.buf16.data[9:9],   hdr.buf16.data[8:8],
            hdr.buf16.data[7:7],   hdr.buf16.data[6:6],   hdr.buf16.data[5:5],   hdr.buf16.data[4:4],
            hdr.buf16.data[3:3],   hdr.buf16.data[2:2],   hdr.buf16.data[1:1],   hdr.buf16.data[0:0],
            hdr.buf16.data[15:15], hdr.buf16.data[14:14], hdr.buf16.data[13:13], hdr.buf16.data[12:12],
            hdr.buf16.data[11:11], hdr.buf16.data[10:10], hdr.buf16.data[9:9],   hdr.buf16.data[8:8],
            hdr.buf16.data[7:7],   hdr.buf16.data[6:6],   hdr.buf16.data[5:5],   hdr.buf16.data[4:4],
            hdr.buf16.data[3:3],   hdr.buf16.data[2:2],   hdr.buf16.data[1:1],   hdr.buf16.data[0:0]
        ) {
            (
                _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _,
                _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _,
                _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _,
                _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _
            ) : State_1_suff_0;

            default: reject;
        }
    }

    state State_1_suff_0 {
        pkt.extract(hdr.buf128);
        transition accept;
    }

    state State_2 {
        pkt.extract(hdr.buf16);
        transition select (
            hdr.buf16.data[15:15], hdr.buf16.data[14:14], hdr.buf16.data[13:13], hdr.buf16.data[12:12],
            hdr.buf16.data[11:11], hdr.buf16.data[10:10], hdr.buf16.data[9:9],   hdr.buf16.data[8:8],
            hdr.buf16.data[7:7],   hdr.buf16.data[6:6],   hdr.buf16.data[5:5],   hdr.buf16.data[4:4],
            hdr.buf16.data[3:3],   hdr.buf16.data[2:2],   hdr.buf16.data[1:1],   hdr.buf16.data[0:0],
            hdr.buf16.data[15:15], hdr.buf16.data[14:14], hdr.buf16.data[13:13], hdr.buf16.data[12:12],
            hdr.buf16.data[11:11], hdr.buf16.data[10:10], hdr.buf16.data[9:9],   hdr.buf16.data[8:8],
            hdr.buf16.data[7:7],   hdr.buf16.data[6:6],   hdr.buf16.data[5:5],   hdr.buf16.data[4:4],
            hdr.buf16.data[3:3],   hdr.buf16.data[2:2],   hdr.buf16.data[1:1],   hdr.buf16.data[0:0],
            hdr.buf16.data[15:15], hdr.buf16.data[14:14], hdr.buf16.data[13:13], hdr.buf16.data[12:12],
            hdr.buf16.data[11:11], hdr.buf16.data[10:10], hdr.buf16.data[9:9],   hdr.buf16.data[8:8],
            hdr.buf16.data[7:7],   hdr.buf16.data[6:6],   hdr.buf16.data[5:5],   hdr.buf16.data[4:4],
            hdr.buf16.data[3:3],   hdr.buf16.data[2:2],   hdr.buf16.data[1:1],   hdr.buf16.data[0:0],
            hdr.buf16.data[15:15], hdr.buf16.data[14:14], hdr.buf16.data[13:13], hdr.buf16.data[12:12],
            hdr.buf16.data[11:11], hdr.buf16.data[10:10], hdr.buf16.data[9:9],   hdr.buf16.data[8:8],
            hdr.buf16.data[7:7],   hdr.buf16.data[6:6],   hdr.buf16.data[5:5],   hdr.buf16.data[4:4],
            hdr.buf16.data[3:3],   hdr.buf16.data[2:2],   hdr.buf16.data[1:1],   hdr.buf16.data[0:0]
        ) {
            (
                _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _,
                _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _,
                _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _,
                _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _
            ) : State_2_suff_0;

            default: reject;
        }
    }

    state State_2_suff_0 {
        pkt.extract(hdr.buf304);
        transition accept;
    }

    state State_3 {
        pkt.extract(hdr.buf16);
        transition select (
            hdr.buf16.data[15:15], hdr.buf16.data[14:14], hdr.buf16.data[13:13], hdr.buf16.data[12:12],
            hdr.buf16.data[11:11], hdr.buf16.data[10:10], hdr.buf16.data[9:9],   hdr.buf16.data[8:8],
            hdr.buf16.data[7:7],   hdr.buf16.data[6:6],   hdr.buf16.data[5:5],   hdr.buf16.data[4:4],
            hdr.buf16.data[3:3],   hdr.buf16.data[2:2],   hdr.buf16.data[1:1],   hdr.buf16.data[0:0],
            hdr.buf16.data[15:15], hdr.buf16.data[14:14], hdr.buf16.data[13:13], hdr.buf16.data[12:12],
            hdr.buf16.data[11:11], hdr.buf16.data[10:10], hdr.buf16.data[9:9],   hdr.buf16.data[8:8],
            hdr.buf16.data[7:7],   hdr.buf16.data[6:6],   hdr.buf16.data[5:5],   hdr.buf16.data[4:4],
            hdr.buf16.data[3:3],   hdr.buf16.data[2:2],   hdr.buf16.data[1:1],   hdr.buf16.data[0:0],
            hdr.buf16.data[15:15], hdr.buf16.data[14:14], hdr.buf16.data[13:13], hdr.buf16.data[12:12],
            hdr.buf16.data[11:11], hdr.buf16.data[10:10], hdr.buf16.data[9:9],   hdr.buf16.data[8:8],
            hdr.buf16.data[7:7],   hdr.buf16.data[6:6],   hdr.buf16.data[5:5],   hdr.buf16.data[4:4],
            hdr.buf16.data[3:3],   hdr.buf16.data[2:2],   hdr.buf16.data[1:1],   hdr.buf16.data[0:0],
            hdr.buf16.data[15:15], hdr.buf16.data[14:14], hdr.buf16.data[13:13], hdr.buf16.data[12:12],
            hdr.buf16.data[11:11], hdr.buf16.data[10:10], hdr.buf16.data[9:9],   hdr.buf16.data[8:8],
            hdr.buf16.data[7:7],   hdr.buf16.data[6:6],   hdr.buf16.data[5:5],   hdr.buf16.data[4:4],
            hdr.buf16.data[3:3],   hdr.buf16.data[2:2],   hdr.buf16.data[1:1],   hdr.buf16.data[0:0]
        ) {
            (
                _, _, _, _, 0, 1, 0, 1, _, _, _, _, _, _, _, _,
                _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _,
                _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _,
                _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _
            ) : State_3_suff_0;

            (
                _, _, _, _, 0, 1, 1, 0, _, _, _, _, _, _, _, _,
                _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _,
                _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _,
                _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _
            ) : State_3_suff_1;

            (
                _, _, _, _, 0, 1, 1, 1, _, _, _, _, _, _, _, _,
                _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _,
                _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _,
                _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _
            ) : State_3_suff_2;

            (
                _, _, _, _, 1, 0, 0, 0, _, _, _, _, _, _, _, _,
                _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _,
                _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _,
                _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _
            ) : State_3_suff_3;

            default: reject;
        }
    }

    state State_3_suff_0 {
        pkt.extract(hdr.buf144);
        transition accept;
    }

    state State_3_suff_1 {
        pkt.extract(hdr.buf176);
        transition accept;
    }

    state State_3_suff_2 {
        pkt.extract(hdr.buf208);
        transition accept;
    }

    state State_3_suff_3 {
        pkt.extract(hdr.buf240);
        transition accept;
    }

    state State_4 {
        pkt.extract(hdr.buf64);
        transition select (
            hdr.buf64.data[15:15], hdr.buf64.data[14:14], hdr.buf64.data[13:13], hdr.buf64.data[12:12],
            hdr.buf64.data[11:11], hdr.buf64.data[10:10], hdr.buf64.data[9:9],   hdr.buf64.data[8:8],
            hdr.buf64.data[7:7],   hdr.buf64.data[6:6],   hdr.buf64.data[5:5],   hdr.buf64.data[4:4],
            hdr.buf64.data[3:3],   hdr.buf64.data[2:2],   hdr.buf64.data[1:1],   hdr.buf64.data[0:0],
            hdr.buf64.data[31:31], hdr.buf64.data[30:30], hdr.buf64.data[29:29], hdr.buf64.data[28:28],
            hdr.buf64.data[27:27], hdr.buf64.data[26:26], hdr.buf64.data[25:25], hdr.buf64.data[24:24],
            hdr.buf64.data[23:23], hdr.buf64.data[22:22], hdr.buf64.data[21:21], hdr.buf64.data[20:20],
            hdr.buf64.data[19:19], hdr.buf64.data[18:18], hdr.buf64.data[17:17], hdr.buf64.data[16:16],
            hdr.buf64.data[47:47], hdr.buf64.data[46:46], hdr.buf64.data[45:45], hdr.buf64.data[44:44],
            hdr.buf64.data[43:43], hdr.buf64.data[42:42], hdr.buf64.data[41:41], hdr.buf64.data[40:40],
            hdr.buf64.data[39:39], hdr.buf64.data[38:38], hdr.buf64.data[37:37], hdr.buf64.data[36:36],
            hdr.buf64.data[35:35], hdr.buf64.data[34:34], hdr.buf64.data[33:33], hdr.buf64.data[32:32],
            hdr.buf64.data[63:63], hdr.buf64.data[62:62], hdr.buf64.data[61:61], hdr.buf64.data[60:60],
            hdr.buf64.data[59:59], hdr.buf64.data[58:58], hdr.buf64.data[57:57], hdr.buf64.data[56:56],
            hdr.buf64.data[55:55], hdr.buf64.data[54:54], hdr.buf64.data[53:53], hdr.buf64.data[52:52],
            hdr.buf64.data[51:51], hdr.buf64.data[50:50], hdr.buf64.data[49:49], hdr.buf64.data[48:48]
        ) {
            (
                _, _, _, _, _, _, _, 0,
                _, _, _, _, _, _, _, _,
                _, _, _, _, _, _, _, _,
                _, _, _, _, _, _, _, _,
                _, _, _, _, _, _, _, 1,
                _, _, _, _, _, _, _, _,
                0, 0, 0, 0, _, _, _, _,
                _, _, _, _, _, _, _, _
            ) : reject;

            (
                _, _, _, _, _, _, _, 0,
                _, _, _, _, _, _, _, _,
                _, _, _, _, _, _, _, _,
                _, _, _, _, _, _, _, _,
                _, _, _, _, _, _, _, 1,
                _, _, _, _, _, _, _, _,
                0, 1, 0, 0, _, _, _, _,
                _, _, _, _, _, _, _, _
            ) : reject;

            (
                _, _, _, _, _, _, _, 0,
                _, _, _, _, _, _, _, _,
                _, _, _, _, _, _, _, _,
                _, _, _, _, _, _, _, _,
                _, _, _, _, _, _, _, 1,
                _, _, _, _, _, _, _, _,
                0, 1, 1, 0, _, _, _, _,
                _, _, _, _, _, _, _, _
            ) : reject;

            (
                _, _, _, _, _, _, _, 0,
                _, _, _, _, _, _, _, _,
                _, _, _, _, _, _, _, _,
                _, _, _, _, _, _, _, _,
                _, _, _, _, _, _, _, _,
                _, _, _, _, _, _, _, _,
                _, _, _, _, _, _, _, _,
                _, _, _, _, _, _, _, _
            ) : reject;

            (
                _, _, _, _, _, _, _, 1,
                _, _, _, _, _, _, _, _,
                0, 0, 0, 0, _, _, _, _,
                _, _, _, _, _, _, _, _,
                _, _, _, _, _, _, _, _,
                _, _, _, _, _, _, _, _,
                _, _, _, _, _, _, _, _,
                _, _, _, _, _, _, _, _
            ) : reject;

            (
                _, _, _, _, _, _, _, 1,
                _, _, _, _, _, _, _, _,
                0, 1, 0, 0, _, _, _, _,
                _, _, _, _, _, _, _, _,
                _, _, _, _, _, _, _, _,
                _, _, _, _, _, _, _, _,
                _, _, _, _, _, _, _, _,
                _, _, _, _, _, _, _, _
            ) : reject;

            (
                _, _, _, _, _, _, _, 1,
                _, _, _, _, _, _, _, _,
                0, 1, 1, 0, _, _, _, _,
                _, _, _, _, _, _, _, _,
                _, _, _, _, _, _, _, _,
                _, _, _, _, _, _, _, _,
                _, _, _, _, _, _, _, _,
                _, _, _, _, _, _, _, _
            ) : reject;

            (
                _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _,
                _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _,
                _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _,
                _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _
            ) : reject;

            default: reject;
        }
    }
}

// FOOTER START
parser Parser_t(packet_in pkt, out headers_t hdr);
package Package(Parser_t p);

Package(Parser()) main;
// FOOTER END
