// HEADER START
#include <core.p4>
// HEADER END

#define USE_NATIVE_PRIMITIVE 0
#define USE_RECIRCULATE 1

header ethernet_t {
        bit<48> dstAddr;
        bit<48> srcAddr;
        bit<16> etherType;
}

// Field are multiple of byte to easy the data manipulation
// IP header
header ipv4_t {
        bit<8>  version_ihl;      // [7..4] version, [3..0] ihl
        bit<8>  diffserv;
        bit<16> totalLen;
        bit<16> identification;
        bit<16> flags_fragOffset; // [15..13] flags, fragOffset [12..0]
        bit<8>  ttl;
        bit<8>  protocol;
        bit<16> hdrChecksum;
        bit<32> srcAddr;
        bit<32> dstAddr;
}

// UDP header
header udp_t {
        bit<16> srcPort;
        bit<16> dstPort;
        bit<16> hdrLength;
        bit<16> chksum;
}

// RTP header
header rtp_t {
		bit<8>      version_pad_ext_nCRSC; // [7..6] version, [5] pad, [4] ext, [3..0] nCRSC
	    bit<8>      marker_payloadType;    // [7] marker, [6..0] payloadType
	    bit<16>     sequenceNumber;
	    bit<32>     timestamp;
	    bit<32>     SSRC;
}

// List of all recognized headers
struct parsed_packet {
    ethernet_t ethernet;
    ipv4_t     ipv4;
    udp_t      udp;
    rtp_t      rtp;
}

parser Parser(packet_in b,
				out parsed_packet p) {

    state start {
        b.extract(p.ethernet);
        transition select(p.ethernet.etherType) {
            0x0800 : parse_ipv4;
	default: accept;
            // no default rule: all other packets rejected
        }
    }

    state parse_ipv4 {
        b.extract(p.ipv4);
        transition select(p.ipv4.protocol) {
            0x11      : parse_udp;
	default   : accept;
	}
	}

    state parse_udp {
        b.extract(p.udp);
        transition select(p.udp.dstPort) {
	1234      : parse_rtp;
	1235      : parse_rtp;
	5004      : parse_rtp;
	5005      : parse_rtp;
	default   : accept;
	}
	}

	state parse_rtp {
	    b.extract(p.rtp);
        transition accept;
	}
}

// FOOTER START
parser Parser_t(packet_in b,
				out parsed_packet p);
package Package(Parser_t p);

Package(Parser()) main;
// FOOTER END
