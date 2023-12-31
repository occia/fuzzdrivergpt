# Tested APIs

Currently, the projects and APIs listed in the following table are fully supported for all features provided by `fuzzdrivergpt`. A more general implementaion will come soon.

| Target Project (`-t`)  | Function Signature (`-f`)                |
| --- | --- |
| bind9                  | dns_master_loadbuffer                    |
| bind9                  | dns_message_checksig                     |
| bind9                  | dns_message_parse                        |
| bind9                  | dns_name_fromtext                        |
| bind9                  | dns_name_fromwire                        |
| bind9                  | dns_rdata_fromtext                       |
| bind9                  | dns_rdata_fromwire                       |
| bind9                  | isc_lex_getmastertoken                   |
| bind9                  | isc_lex_gettoken                         |
| civetweb               | mg_get_response                          |
| coturn                 | stun_check_message_integrity_str         |
| coturn                 | stun_is_binding_response                 |
| coturn                 | stun_is_command_message                  |
| coturn                 | stun_is_command_message_full_check_str   |
| coturn                 | stun_is_response                         |
| coturn                 | stun_is_success_response                 |
| croaring               | roaring_bitmap_portable_deserialize_safe |
| gdk-pixbuf             | gdk_pixbuf_animation_new_from_file       |
| gdk-pixbuf             | gdk_pixbuf_new_from_data                 |
| gdk-pixbuf             | gdk_pixbuf_new_from_file                 |
| gdk-pixbuf             | gdk_pixbuf_new_from_file_at_scale        |
| gdk-pixbuf             | gdk_pixbuf_new_from_stream               |
| gpac                   | gf_isom_open_file                        |
| hiredis                | redisFormatCommand                       |
| igraph                 | igraph_all_minimal_st_separators         |
| igraph                 | igraph_automorphism_group                |
| igraph                 | igraph_edge_connectivity                 |
| igraph                 | igraph_minimum_size_separators           |
| igraph                 | igraph_read_graph_dl                     |
| igraph                 | igraph_read_graph_edgelist               |
| igraph                 | igraph_read_graph_gml                    |
| igraph                 | igraph_read_graph_graphdb                |
| igraph                 | igraph_read_graph_graphml                |
| igraph                 | igraph_read_graph_lgl                    |
| igraph                 | igraph_read_graph_ncol                   |
| igraph                 | igraph_read_graph_pajek                  |
| inchi                  | GetINCHIKeyFromINCHI                     |
| inchi                  | GetINCHIfromINCHI                        |
| inchi                  | GetStructFromINCHI                       |
| kamailio               | get_src_address_socket                   |
| kamailio               | get_src_uri                              |
| kamailio               | parse_content_disposition                |
| kamailio               | parse_diversion_header                   |
| kamailio               | parse_from_header                        |
| kamailio               | parse_from_uri                           |
| kamailio               | parse_headers                            |
| kamailio               | parse_identityinfo_header                |
| kamailio               | parse_msg                                |
| kamailio               | parse_pai_header                         |
| kamailio               | parse_privacy                            |
| kamailio               | parse_record_route_headers               |
| kamailio               | parse_refer_to_header                    |
| kamailio               | parse_route_headers                      |
| kamailio               | parse_to_header                          |
| kamailio               | parse_to_uri                             |
| kamailio               | parse_uri                                |
| libbpf                 | bpf_object__open_mem                     |
| libdwarf               | dwarf_init_b                             |
| libdwarf               | dwarf_init_path                          |
| libiec61850            | MmsValue_decodeMmsData                   |
| liblouis               | lou_compileString                        |
| libmodbus              | modbus_read_bits                         |
| libmodbus              | modbus_read_registers                    |
| libmodbus              | modbus_receive                           |
| libpg_query            | pg_query_parse                           |
| libucl                 | ucl_parser_add_string                    |
| libyang                | lyd_parse_data_mem                       |
| libyang                | lys_parse_mem                            |
| libzip                 | zip_fread                                |
| lua                    | luaL_loadbufferx                         |
| md4c                   | md_html                                  |
| oniguruma              | onig_new                                 |
| pjsip                  | pj_json_parse                            |
| pjsip                  | pj_stun_msg_decode                       |
| pjsip                  | pj_xml_parse                             |
| pjsip                  | pjmedia_sdp_parse                        |
| pjsip                  | pjsip_parse_msg                          |
| proftpd                | pr_json_object_from_text                 |
| pupnp                  | ixmlLoadDocumentEx                       |
| quickjs                | JS_Eval                                  |
| quickjs                | lre_compile                              |
| selinux                | cil_compile                              |
| selinux                | policydb_read                            |
| spdk                   | spdk_json_parse                          |
| tmux                   | input_parse_buffer                       |
| w3m                    | wc_Str_conv_with_detect                  |
