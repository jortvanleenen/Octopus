/*
David Hancock
FLUX Research Group
University of Utah
dhancock@cs.utah.edu

HyPer4: A P4 Program to Run Other P4 Programs

headers.p4: Define the headers required by HP4.
*/

header_type csum_t {
  fields {
    sum : 32;
    rshift : 16;
    div : 8;
    final : 16;
    csmask : 768;
  }
}

// Unfortunately, despite the stated goal of HyPer4 to provide target independent features,
//  bmv2 requires this intrinsic metadata structure in order to do a resubmit
header_type intrinsic_metadata_t {
  fields {
        mcast_grp : 4;
        egress_rid : 4;
        mcast_hash : 16;
        lf_field_list : 32;
        resubmit_flag : 16;
        recirculate_flag : 16;
  }
}

header_type parse_ctrl_t {
  fields {
    numbytes : 8;
    state : 12;
    next_action : 4;
  }
}

// meta_ctrl: stores control stage (e.g. INIT, NORM), next table, stage
// state (e.g. CONTINUE, COMPLETE… to track whether a sequence of primitives
// is complete)
header_type meta_ctrl_t {
  fields {
    program : 8; // identifies which program to run
    stage : 1; // INIT, NORM.
    next_table : 4;
    stage_state : 2; // CONTINUE, COMPLETE - 1 bit should be enough, certainly 2
    multicast_current_egress : 8;
    multicast_seq_id : 8;
    stdmeta_ID : 3;
    next_stage : 5;
    mc_flag : 1;
    virt_egress_port : 8;
    virt_ingress_port : 8;
    clone_program : 8;
  }
}

// meta_primitive_state: information about a specific target primitive
header_type meta_primitive_state_t {
  fields {
    action_ID : 7; // identifies the compound action being executed
    match_ID : 23; // identifies the match entry
    primitive_index : 6; // place within compound action
    primitive : 6; // e.g. modify_field, add_header, etc.
    subtype : 6; // maps to a set identifying the parameters' types
  }
}

// tmeta: HyPer4's representation of the target's metadata
header_type tmeta_t {
  fields {
    data : 256;
  }
}

header_type ext_t {
  fields {
    data : 8;
  }
}

// extracted: stores extracted data in a standard width field
header_type extracted_t {
  fields {
    data : 800;
    validbits : 80;
  }
}


/*
David Hancock
FLUX Research Group
University of Utah
dhancock@cs.utah.edu

HyPer4: A P4 Program to Run Other P4 Programs

parser.p4: Define various parse functions allowing us to extract a specified
           number of bits from the received packet.
*/

metadata parse_ctrl_t parse_ctrl;
header ext_t ext[100];

parser start {
  set_metadata(parse_ctrl.next_action, PROCEED);
  extract(ext[next]);
  extract(ext[next]);
  extract(ext[next]);
  extract(ext[next]);
  extract(ext[next]);
  extract(ext[next]);
  extract(ext[next]);
  extract(ext[next]);
  extract(ext[next]);
  extract(ext[next]);
  extract(ext[next]);
  extract(ext[next]);
  extract(ext[next]);
  extract(ext[next]);
  extract(ext[next]);
  extract(ext[next]);
  extract(ext[next]);
  extract(ext[next]);
  extract(ext[next]);
  extract(ext[next]);
  return select(parse_ctrl.numbytes) {
    0 : ingress;
    20 : ingress;
    21 : pr01;
    22 : pr02;
    23 : pr03;
    24 : pr04;
    25 : pr05;
    26 : pr06;
    27 : pr07;
    28 : pr08;
    29 : pr09;
    default : p30;
  }
}

parser pr01 {
  extract(ext[next]);
  return ingress;
}

parser pr02 {
  extract(ext[next]);
  extract(ext[next]);
  return ingress;
}

parser pr03 {
  extract(ext[next]);
  extract(ext[next]);
  extract(ext[next]);
  return ingress;
}

parser pr04 {
  extract(ext[next]);
  extract(ext[next]);
  extract(ext[next]);
  extract(ext[next]);
  return ingress;
}

parser pr05 {
  extract(ext[next]);
  extract(ext[next]);
  extract(ext[next]);
  extract(ext[next]);
  extract(ext[next]);
  return ingress;
}

parser pr06 {
  extract(ext[next]);
  extract(ext[next]);
  extract(ext[next]);
  extract(ext[next]);
  extract(ext[next]);
  extract(ext[next]);
  return ingress;
}

parser pr07 {
  extract(ext[next]);
  extract(ext[next]);
  extract(ext[next]);
  extract(ext[next]);
  extract(ext[next]);
  extract(ext[next]);
  extract(ext[next]);
  return ingress;
}

parser pr08 {
  extract(ext[next]);
  extract(ext[next]);
  extract(ext[next]);
  extract(ext[next]);
  extract(ext[next]);
  extract(ext[next]);
  extract(ext[next]);
  extract(ext[next]);
  return ingress;
}

parser pr09 {
  extract(ext[next]);
  extract(ext[next]);
  extract(ext[next]);
  extract(ext[next]);
  extract(ext[next]);
  extract(ext[next]);
  extract(ext[next]);
  extract(ext[next]);
  extract(ext[next]);
  return ingress;
}

parser p30 {
  extract(ext[next]);
  extract(ext[next]);
  extract(ext[next]);
  extract(ext[next]);
  extract(ext[next]);
  extract(ext[next]);
  extract(ext[next]);
  extract(ext[next]);
  extract(ext[next]);
  extract(ext[next]);
  return select(parse_ctrl.numbytes) {
    30 : ingress;
    31 : pr01;
    32 : pr02;
    33 : pr03;
    34 : pr04;
    35 : pr05;
    36 : pr06;
    37 : pr07;
    38 : pr08;
    39 : pr09;
    default : p40;
  }
}

parser p40 {
  extract(ext[next]);
  extract(ext[next]);
  extract(ext[next]);
  extract(ext[next]);
  extract(ext[next]);
  extract(ext[next]);
  extract(ext[next]);
  extract(ext[next]);
  extract(ext[next]);
  extract(ext[next]);
  return select(parse_ctrl.numbytes) {
    40 : ingress;
    41 : pr01;
    42 : pr02;
    43 : pr03;
    44 : pr04;
    45 : pr05;
    46 : pr06;
    47 : pr07;
    48 : pr08;
    49 : pr09;
    default : p50;
  }
}

parser p50 {
  extract(ext[next]);
  extract(ext[next]);
  extract(ext[next]);
  extract(ext[next]);
  extract(ext[next]);
  extract(ext[next]);
  extract(ext[next]);
  extract(ext[next]);
  extract(ext[next]);
  extract(ext[next]);
  return select(parse_ctrl.numbytes) {
    50 : ingress;
    51 : pr01;
    52 : pr02;
    53 : pr03;
    54 : pr04;
    55 : pr05;
    56 : pr06;
    57 : pr07;
    58 : pr08;
    59 : pr09;
    default : p60;
  }
}

parser p60 {
  extract(ext[next]);
  extract(ext[next]);
  extract(ext[next]);
  extract(ext[next]);
  extract(ext[next]);
  extract(ext[next]);
  extract(ext[next]);
  extract(ext[next]);
  extract(ext[next]);
  extract(ext[next]);
  return select(parse_ctrl.numbytes) {
    60 : ingress;
    61 : pr01;
    62 : pr02;
    63 : pr03;
    64 : pr04;
    65 : pr05;
    66 : pr06;
    67 : pr07;
    68 : pr08;
    69 : pr09;
    default : p70;
  }
}

parser p70 {
  extract(ext[next]);
  extract(ext[next]);
  extract(ext[next]);
  extract(ext[next]);
  extract(ext[next]);
  extract(ext[next]);
  extract(ext[next]);
  extract(ext[next]);
  extract(ext[next]);
  extract(ext[next]);
  return select(parse_ctrl.numbytes) {
    70 : ingress;
    71 : pr01;
    72 : pr02;
    73 : pr03;
    74 : pr04;
    75 : pr05;
    76 : pr06;
    77 : pr07;
    78 : pr08;
    79 : pr09;
    default : p80;
  }
}

parser p80 {
  extract(ext[next]);
  extract(ext[next]);
  extract(ext[next]);
  extract(ext[next]);
  extract(ext[next]);
  extract(ext[next]);
  extract(ext[next]);
  extract(ext[next]);
  extract(ext[next]);
  extract(ext[next]);
  return select(parse_ctrl.numbytes) {
    80 : ingress;
    81 : pr01;
    82 : pr02;
    83 : pr03;
    84 : pr04;
    85 : pr05;
    86 : pr06;
    87 : pr07;
    88 : pr08;
    89 : pr09;
    default : p90;
  }
}

parser p90 {
  extract(ext[next]);
  extract(ext[next]);
  extract(ext[next]);
  extract(ext[next]);
  extract(ext[next]);
  extract(ext[next]);
  extract(ext[next]);
  extract(ext[next]);
  extract(ext[next]);
  extract(ext[next]);
  return select(parse_ctrl.numbytes) {
    90 : ingress;
    91 : pr01;
    92 : pr02;
    93 : pr03;
    94 : pr04;
    95 : pr05;
    96 : pr06;
    97 : pr07;
    98 : pr08;
    99 : pr09;
    default : p100;
  }
}

parser p100 {
  extract(ext[next]);
  extract(ext[next]);
  extract(ext[next]);
  extract(ext[next]);
  extract(ext[next]);
  extract(ext[next]);
  extract(ext[next]);
  extract(ext[next]);
  extract(ext[next]);
  extract(ext[next]);
  return ingress;
}