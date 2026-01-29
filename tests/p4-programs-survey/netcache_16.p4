// HEADER START
#include <core.p4>
// HEADER END

struct hh_bf_md_t {
    bit<16> index_1;
    bit<16> index_2;
    bit<16> index_3;
    bit<1>  bf_1;
    bit<1>  bf_2;
    bit<1>  bf_3;
}

struct nc_cache_md_t {
    bit<1>  cache_exist;
    bit<14> cache_index;
    bit<1>  cache_valid;
}

struct nc_load_md_t {
    bit<16> index_1;
    bit<16> index_2;
    bit<16> index_3;
    bit<16> index_4;
    bit<32> load_1;
    bit<32> load_2;
    bit<32> load_3;
    bit<32> load_4;
}

struct reply_read_hit_info_md_t {
    bit<32> ipv4_srcAddr;
    bit<32> ipv4_dstAddr;
}

header ethernet_t {
    bit<48> dstAddr;
    bit<48> srcAddr;
    bit<16> etherType;
}

header ipv4_t {
    bit<4>  version;
    bit<4>  ihl;
    bit<8>  diffserv;
    bit<16> totalLen;
    bit<16> identification;
    bit<3>  flags;
    bit<13> fragOffset;
    bit<8>  ttl;
    bit<8>  protocol;
    bit<16> hdrChecksum;
    bit<32> srcAddr;
    bit<32> dstAddr;
}

header nc_hdr_t {
    bit<8>   op;
    bit<128> key;
}

header nc_load_t {
    bit<32> load_1;
    bit<32> load_2;
    bit<32> load_3;
    bit<32> load_4;
}

header nc_value_1_t {
    bit<32> value_1_1;
    bit<32> value_1_2;
    bit<32> value_1_3;
    bit<32> value_1_4;
}

header nc_value_2_t {
    bit<32> value_2_1;
    bit<32> value_2_2;
    bit<32> value_2_3;
    bit<32> value_2_4;
}

header nc_value_3_t {
    bit<32> value_3_1;
    bit<32> value_3_2;
    bit<32> value_3_3;
    bit<32> value_3_4;
}

header nc_value_4_t {
    bit<32> value_4_1;
    bit<32> value_4_2;
    bit<32> value_4_3;
    bit<32> value_4_4;
}

header nc_value_5_t {
    bit<32> value_5_1;
    bit<32> value_5_2;
    bit<32> value_5_3;
    bit<32> value_5_4;
}

header nc_value_6_t {
    bit<32> value_6_1;
    bit<32> value_6_2;
    bit<32> value_6_3;
    bit<32> value_6_4;
}

header nc_value_7_t {
    bit<32> value_7_1;
    bit<32> value_7_2;
    bit<32> value_7_3;
    bit<32> value_7_4;
}

header nc_value_8_t {
    bit<32> value_8_1;
    bit<32> value_8_2;
    bit<32> value_8_3;
    bit<32> value_8_4;
}

header tcp_t {
    bit<16> srcPort;
    bit<16> dstPort;
    bit<32> seqNo;
    bit<32> ackNo;
    bit<4>  dataOffset;
    bit<3>  res;
    bit<3>  ecn;
    bit<6>  ctrl;
    bit<16> window;
    bit<16> checksum;
    bit<16> urgentPtr;
}

header udp_t {
    bit<16> srcPort;
    bit<16> dstPort;
    bit<16> len;
    bit<16> checksum;
}

struct headers {
    @name(".ethernet") 
    ethernet_t   ethernet;
    @name(".ipv4") 
    ipv4_t       ipv4;
    @name(".nc_hdr") 
    nc_hdr_t     nc_hdr;
    @name(".nc_load") 
    nc_load_t    nc_load;
    @name(".nc_value_1") 
    nc_value_1_t nc_value_1;
    @name(".nc_value_2") 
    nc_value_2_t nc_value_2;
    @name(".nc_value_3") 
    nc_value_3_t nc_value_3;
    @name(".nc_value_4") 
    nc_value_4_t nc_value_4;
    @name(".nc_value_5") 
    nc_value_5_t nc_value_5;
    @name(".nc_value_6") 
    nc_value_6_t nc_value_6;
    @name(".nc_value_7") 
    nc_value_7_t nc_value_7;
    @name(".nc_value_8") 
    nc_value_8_t nc_value_8;
    @name(".tcp") 
    tcp_t        tcp;
    @name(".udp") 
    udp_t        udp;
}

parser Parser(packet_in packet, out headers hdr) {
    @name(".start") state start {
        packet.extract(hdr.ethernet);
        transition select(hdr.ethernet.etherType) {
            16w0x800: parse_ipv4;
            default: accept;
        }
    }
    @name(".parse_ipv4") state parse_ipv4 {
        packet.extract(hdr.ipv4);
        transition select(hdr.ipv4.protocol) {
            8w6: parse_tcp;
            8w17: parse_udp;
            default: accept;
        }
    }
    @name(".parse_nc_hdr") state parse_nc_hdr {
        packet.extract(hdr.nc_hdr);
        transition select(hdr.nc_hdr.op) {
            8w0: accept;
            8w1: parse_nc_value_1;
            8w2: parse_nc_load;
            8w8: accept;
            8w9: parse_nc_value_1;
            default: accept;
        }
    }
    @name(".parse_nc_load") state parse_nc_load {
        packet.extract(hdr.nc_load);
        transition accept;
    }
    @name(".parse_nc_value_1") state parse_nc_value_1 {
        packet.extract(hdr.nc_value_1);
        transition parse_nc_value_2;
    }
    @name(".parse_nc_value_2") state parse_nc_value_2 {
        packet.extract(hdr.nc_value_2);
        transition parse_nc_value_3;
    }
    @name(".parse_nc_value_3") state parse_nc_value_3 {
        packet.extract(hdr.nc_value_3);
        transition parse_nc_value_4;
    }
    @name(".parse_nc_value_4") state parse_nc_value_4 {
        packet.extract(hdr.nc_value_4);
        transition parse_nc_value_5;
    }
    @name(".parse_nc_value_5") state parse_nc_value_5 {
        packet.extract(hdr.nc_value_5);
        transition parse_nc_value_6;
    }
    @name(".parse_nc_value_6") state parse_nc_value_6 {
        packet.extract(hdr.nc_value_6);
        transition parse_nc_value_7;
    }
    @name(".parse_nc_value_7") state parse_nc_value_7 {
        packet.extract(hdr.nc_value_7);
        transition parse_nc_value_8;
    }
    @name(".parse_nc_value_8") state parse_nc_value_8 {
        packet.extract(hdr.nc_value_8);
        transition accept;
    }
    @name(".parse_tcp") state parse_tcp {
        packet.extract(hdr.tcp);
        transition accept;
    }
    @name(".parse_udp") state parse_udp {
        packet.extract(hdr.udp);
        transition select(hdr.udp.dstPort) {
            16w8888: parse_nc_hdr;
            default: accept;
        }
    }
}

// FOOTER START
parser Parser_t(packet_in packet, out headers hdr);
package Package(Parser_t p);

Package(Parser()) main;
// FOOTER END
