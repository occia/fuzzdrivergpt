'''
partial api doc prepared manually
TODO: make this automatically analyzed later
'''
manualapidocs = {
	"libzip": {
"zip_fread": '''
/*
 * DESCRIPTION
 * The zip_fread() function reads up to nbytes bytes from file into buf.
 * 
 * RETURN VALUES
 * If successful, the number of bytes actually read is returned. When zip_fread() is called after reaching the end of the file, 0 is returned. In case of error, -1 is returned.
 */
''',
	},
	"civetweb": {
"mg_get_response": '''
/*
 * ### Parameters
 * 
 * | Parameter | Type | Description |
 * | :--- | :--- | :--- |
 * |**`conn`**|`struct mg_connection *`|The connection to listen on|
 * |**`ebuf`**|`char *`|Buffer to store an error message|
 * |**`ebuf_len`**|`size_t`|Size of the error message buffer including the terminating NUL|
 * |**`timeout`**|`int`|Time to wait for a response in milliseconds|
 * 
 * ### Return Value
 * 
 * | Type | Description |
 * | :--- | :--- |
 * |`int`|Success value of the wait|
 * 
 * ### Description
 * 
 * The function `mg_get_reponse()` wait for a response from a remote server. A return value equal or greater than zero is an indication for success, a negative value us used to signal an error condition. A timeout can be specified which lets the function return after a specified number of milliseconds, even if no data is received from the remote party. If the timeout value is negative, the function will not return until data has been read or an unrecoverable error occurs.
 * 
 * Error messages are stored in a caller supplied error message buffer.
 */
''',
	},
	"gdk-pixbuf": {
"gdk_pixbuf_animation_new_from_file": '''
/*
 * Creates a new animation by loading it from a file. The file format is detected automatically. If the file's format does not support multi-frame images, then an animation with a single frame will be created. Possible errors are in the GDK_PIXBUF_ERROR and G_FILE_ERROR domains.
 * 
 * Parameters
 * filename
 * 
 * Name of file to load, in the GLib file name encoding
 * 
 *  
 * error
 * 
 * return location for error
 * 
 *  
 * Returns
 * A newly-created animation with a reference count of 1, or NULL if any of several error conditions ocurred: the file could not be opened, there was no loader for the file's format, there was not enough memory to allocate the image buffer, or the image file contained invalid data.
 */
''',
"gdk_pixbuf_new_from_data": '''
/*
 * Creates a new GdkPixbuf out of in-memory image data. Currently only RGB images with 8 bits per sample are supported.
 * 
 * Since you are providing a pre-allocated pixel buffer, you must also specify a way to free that data. This is done with a function of type GdkPixbufDestroyNotify. When a pixbuf created with is finalized, your destroy notification function will be called, and it is its responsibility to free the pixel array.
 * 
 * See also gdk_pixbuf_new_from_bytes().
 * 
 * Parameters
 * data
 * 
 * Image data in 8-bit/sample packed format.
 * 
 * [array]
 * colorspace
 * 
 * Colorspace for the image data
 * 
 *  
 * has_alpha
 * 
 * Whether the data has an opacity channel
 * 
 *  
 * bits_per_sample
 * 
 * Number of bits per sample
 * 
 *  
 * width
 * 
 * Width of the image in pixels, must be > 0
 * 
 *  
 * height
 * 
 * Height of the image in pixels, must be > 0
 * 
 *  
 * rowstride
 * 
 * Distance in bytes between row starts
 * 
 *  
 * destroy_fn
 * 
 * Function used to free the data when the pixbuf's reference count drops to zero, or NULL if the data should not be freed.
 * 
 * [scope async][allow-none]
 * destroy_fn_data
 * 
 * Closure data to pass to the destroy notification function.
 * 
 * [closure]
 * Returns
 * A newly-created GdkPixbuf structure with a reference count of 1.
 */
''',
"gdk_pixbuf_new_from_file": '''
/*
 * Creates a new pixbuf by loading an image from a file. The file format is detected automatically. If NULL is returned, then error will be set. Possible errors are in the GDK_PIXBUF_ERROR and G_FILE_ERROR domains.
 * 
 * Parameters
 * filename
 * 
 * Name of file to load, in the GLib file name encoding
 * 
 *  
 * error
 * 
 * Return location for an error
 * 
 *  
 * Returns
 * A newly-created pixbuf with a reference count of 1, or NULL if any of several error conditions occurred: the file could not be opened, there was no loader for the file's format, there was not enough memory to allocate the image buffer, or the image file contained invalid data.
*/
''',
"gdk_pixbuf_new_from_file_at_scale": '''
/*
 * Creates a new pixbuf by loading an image from a file. The file format is detected automatically. If NULL is returned, then error will be set. Possible errors are in the GDK_PIXBUF_ERROR and G_FILE_ERROR domains. The image will be scaled to fit in the requested size, optionally preserving the image's aspect ratio.
 * 
 * When preserving the aspect ratio, a width of -1 will cause the image to be scaled to the exact given height, and a height of -1 will cause the image to be scaled to the exact given width. When not preserving aspect ratio, a width or height of -1 means to not scale the image at all in that dimension. Negative values for width and height are allowed since 2.8.
 * 
 * Parameters
 * filename
 * 
 * Name of file to load, in the GLib file name encoding
 * 
 *  
 * width
 * 
 * The width the image should have or -1 to not constrain the width
 * 
 *  
 * height
 * 
 * The height the image should have or -1 to not constrain the height
 * 
 *  
 * preserve_aspect_ratio
 * 
 * TRUE to preserve the image's aspect ratio
 * 
 *  
 * error
 * 
 * Return location for an error
 * 
 *  
 * Returns
 * A newly-created pixbuf with a reference count of 1, or NULL if any of several error conditions occurred: the file could not be opened, there was no loader for the file's format, there was not enough memory to allocate the image buffer, or the image file contained invalid data.
 */
''',
"gdk_pixbuf_new_from_stream": '''
/*
 * Creates a new pixbuf by loading an image from an input stream.
 * 
 * The file format is detected automatically. If NULL is returned, then error will be set. The cancellable can be used to abort the operation from another thread. If the operation was cancelled, the error G_IO_ERROR_CANCELLED will be returned. Other possible errors are in the GDK_PIXBUF_ERROR and G_IO_ERROR domains.
 * 
 * The stream is not closed.
 * 
 * Parameters
 * stream
 * 
 * a GInputStream to load the pixbuf from
 * 
 *  
 * cancellable
 * 
 * optional GCancellable object, NULL to ignore.
 * 
 * [allow-none]
 * error
 * 
 * Return location for an error
 * 
 *  
 * Returns
 * A newly-created pixbuf, or NULL if any of several error conditions occurred: the file could not be opened, the image format is not supported, there was not enough memory to allocate the image buffer, the stream contained invalid data, or the operation was cancelled.
*/
''',
	},
	"hiredis": {
"xxx": '''
/* Format a command according to the Redis protocol. This function
 * takes a format similar to printf:
 *
 * %s represents a C null terminated string you want to interpolate
 * %b represents a binary safe string
 *
 * When using %b you need to provide both the pointer to the string
 * and the length in bytes as a size_t. Examples:
 *
 * len = redisFormatCommand(target, "GET %s", mykey);
 * len = redisFormatCommand(target, "SET %s %b", mykey, myval, myvallen);
 */
''',
	},
	"igraph": {
"igraph_all_minimal_st_separators": '''
/**
 * \function igraph_all_minimal_st_separators
 * \brief List all vertex sets that are minimal (s,t) separators for some s and t.
 *
 * This function lists all vertex sets that are minimal (s,t)
 * separators for some (s,t) vertex pair.
 *
 * </para><para>
 * Note that some vertex sets returned by this function may not be minimal
 * with respect to disconnecting the graph (or increasing the number of
 * connected components). Take for example the 5-vertex graph with edges
 * <code>0-1-2-3-4-1</code>. This function returns the vertex sets
 * <code>{1}</code>, <code>{2,4}</code> and <code>{1,3}</code>.
 * Notice that <code>{1,3}</code> is not minimal with respect to disconnecting
 * the graph, as <code>{1}</code> would be sufficient for that. However, it is
 * minimal with respect to separating vertices \c 2 and \c 4.
 *
 * </para><para>
 * See more about the implemented algorithm in
 * Anne Berry, Jean-Paul Bordat and Olivier Cogis: Generating All the
 * Minimal Separators of a Graph, In: Peter Widmayer, Gabriele Neyer
 * and Stephan Eidenbenz (editors): Graph-theoretic concepts in
 * computer science, 1665, 167--172, 1999. Springer.
 * https://doi.org/10.1007/3-540-46784-X_17
 *
 * \param graph The input graph. It may be directed, but edge
 *        directions are ignored.
 * \param separators An initialized pointer vector, the separators
 *        are stored here. It is a list of pointers to <type>igraph_vector_int_t</type>
 *        objects. Each vector will contain the ids of the vertices in
 *        the separator.
 *        To free all memory allocated for \p separators, you need call
 *        \ref igraph_vector_destroy() and then \ref igraph_free() on
 *        each element, before destroying the pointer vector itself.
 * \return Error code.
 *
 * \sa \ref igraph_minimum_size_separators()
 *
 * Time complexity: O(n|V|^3), |V| is the number of vertices, n is the
 * number of separators.
 *
 * \example examples/simple/igraph_minimal_separators.c
 */
''',
"igraph_automorphism_group": '''
/**
 * \function igraph_automorphism_group
 * \brief Automorphism group generators using Bliss.
 *
 * The generators of the automorphism group of a graph are computed
 * using Bliss. The generator set may not be minimal and may depend on
 * the splitting heuristics. The generators are permutations represented
 * using zero-based indexing.
 *
 * \param graph The input graph. Multiple edges between the same nodes
 *   are not supported and will cause an incorrect result to be returned.
 * \param colors An optional vertex color vector for the graph. Supply a
 *   null pointer is the graph is not colored.
 * \param generators Must be an initialized pointer vector. It will
 *    contain pointers to \ref igraph_vector_int_t objects
 *    representing generators of the automorphism group.
 * \param sh The splitting heuristics to be used in Bliss. See \ref
 *    igraph_bliss_sh_t.
 * \param info If not \c NULL then information on Bliss internals is
 *    stored here. The memory used by this structure must to be freed
 *    when no longer needed, see \ref igraph_bliss_info_t.
 * \return Error code.
 *
 * Time complexity: exponential, in practice it is fast for many graphs.
 */
''',
"igraph_edge_connectivity": '''
/**
 * \function igraph_edge_connectivity
 * \brief The minimum edge connectivity in a graph.
 *
 * </para><para> This is the minimum of the edge connectivity over all
 * pairs of vertices in the graph. </para>
 *
 * <para>
 * The edge connectivity of a graph is the same as group adhesion as
 * defined in Douglas R. White and Frank Harary: The cohesiveness of
 * blocks in social networks: node connectivity and conditional
 * density, Sociological Methodology 31:305--359, 2001
 * https://doi.org/10.1111/0081-1750.00098.
 *
 * \param graph The input graph.
 * \param res Pointer to an integer, the result will be stored here.
 * \param checks Logical constant. Whether to check that the graph is
 *    connected and also the degree of the vertices. If the graph is
 *    not (strongly) connected then the connectivity is obviously zero. Otherwise
 *    if the minimum degree is one then the edge connectivity is also
 *    one. It is a good idea to perform these checks, as they can be
 *    done quickly compared to the connectivity calculation itself.
 *    They were suggested by Peter McMahan, thanks Peter.
 * \return Error code.
 *
 * Time complexity: O(log(|V|)*|V|^2) for undirected graphs and
 * O(|V|^4) for directed graphs, but see also the discussion at the
 * documentation of \ref igraph_maxflow_value().
 *
 * \sa \ref igraph_st_edge_connectivity(), \ref igraph_maxflow_value(),
 * \ref igraph_vertex_connectivity().
 */
''',
"igraph_minimum_size_separators": '''
/**
 * \function igraph_minimum_size_separators
 * \brief Find all minimum size separating vertex sets.
 *
 * This function lists all separator vertex sets of minimum size.
 * A vertex set is a separator if its removal disconnects the graph.
 *
 * </para><para>
 * The implementation is based on the following paper:
 * Arkady Kanevsky: Finding all minimum-size separating vertex sets in
 * a graph, Networks 23, 533--541, 1993.
 *
 * \param graph The input graph, which must be undirected.
 * \param separators An initialized list of integer vectors, the separators
 *        are stored here. It is a list of pointers to igraph_vector_int_t
 *        objects. Each vector will contain the IDs of the vertices in
 *        the separator. The separators are returned in an arbitrary order.
 * \return Error code.
 *
 * Time complexity: TODO.
 *
 * \example examples/simple/igraph_minimum_size_separators.c
 */
''',
"igraph_read_graph_dl": '''
/**
 * \function igraph_read_graph_dl
 * \brief Reads a file in the DL format of UCINET.
 *
 * This is a simple textual file format used by UCINET. See
 * http://www.analytictech.com/networks/dataentry.htm for
 * examples. All the forms described here are supported by
 * igraph. Vertex names and edge weights are also supported and they
 * are added as attributes. (If an attribute handler is attached.)
 *
 * </para><para> Note the specification does not mention whether the
 * format is case sensitive or not. For igraph DL files are case
 * sensitive, i.e. \c Larry and \c larry are not the same.
 * \param graph Pointer to an uninitialized graph object.
 * \param instream The stream to read the DL file from.
 * \param directed Logical scalar, whether to create a directed file.
 * \return Error code.
 *
 * Time complexity: linear in terms of the number of edges and
 * vertices, except for the matrix format, which is quadratic in the
 * number of vertices.
 *
 * \example examples/simple/igraph_read_graph_dl.c
 */
''',
"igraph_read_graph_edgelist": '''
/**
 * \ingroup loadsave
 * \function igraph_read_graph_edgelist
 * \brief Reads an edge list from a file and creates a graph.
 *
 * </para><para>
 * This format is simply a series of an even number of non-negative integers separated by
 * whitespace. The integers represent vertex IDs. Placing each edge (i.e. pair of integers)
 * on a separate line is not required, but it is recommended for readability.
 * Edges of directed graphs are assumed to be in "from, to" order.
 *
 * \param graph Pointer to an uninitialized graph object.
 * \param instream Pointer to a stream, it should be readable.
 * \param n The number of vertices in the graph. If smaller than the
 *        largest integer in the file it will be ignored. It is thus
 *        safe to supply zero here.
 * \param directed Logical, if true the graph is directed, if false it
 *        will be undirected.
 * \return Error code:
 *         \c IGRAPH_PARSEERROR: if there is a
 *         problem reading the file, or the file is syntactically
 *         incorrect.
 *
 * Time complexity: O(|V|+|E|), the
 * number of vertices plus the number of edges. It is assumed that
 * reading an integer requires O(1) time.
 */
''',
"igraph_read_graph_gml": '''
/**
 * \function igraph_read_graph_gml
 * \brief Read a graph in GML format.
 *
 * GML is a simple textual format, see
 * https://web.archive.org/web/20190207140002/http://www.fim.uni-passau.de/index.php?id=17297%26L=1
 * for details.
 *
 * </para><para>
 * Although all syntactically correct GML can be parsed,
 * we implement only a subset of this format. Some attributes might be
 * ignored. Here is a list of all the differences:
 * \olist
 * \oli Only attributes with a simple type are used: integer, real or
 *      string. If an attribute is composite, i.e. an array or a record,
 *      then it is ignored. When some values of the attribute are simple and
 *      some compound, the composite ones are replaced with a default value
 *      (NaN for numeric, <code>""</code> for string).
 * \oli <code>comment</code> fields are not ignored. They are treated as any
 *      other field and converted to attributes.
 * \oli Top level attributes except for <code>Version</code> and the
 *      first <code>graph</code> attribute are completely ignored.
 * \oli There is no maximum line length or maximum keyword length.
 * \oli Only the \c quot, \c amp, \c apos, \c lt and \c gt character entities
 *      are supported. Any other entity is passed through unchanged by the reader
 *      after issuing a warning, and is expected to be decoded by the user.
 * \oli We allow <code>inf</code>, <code>-inf</code> and <code>nan</code>
 *      (not a number) as a real number. This is case insensitive, so
 *      <code>nan</code>, <code>NaN</code> and <code>NAN</code> are equivalent.
 * \endolist
 *
 * </para><para> Please contact us if you cannot live with these
 * limitations of the GML parser.
 *
 * \param graph Pointer to an uninitialized graph object.
 * \param instream The stream to read the GML file from.
 * \return Error code.
 *
 * Time complexity: should be proportional to the length of the file.
 *
 * \sa \ref igraph_read_graph_graphml() for a more modern format,
 * \ref igraph_write_graph_gml() for writing GML files.
 *
 * \example examples/simple/gml.c
 */
''',
"igraph_read_graph_graphdb": '''
/**
 * \function igraph_read_graph_graphdb
 * \brief Read a graph in the binary graph database format.
 *
 * This is a binary format, used in the ARG Graph Database
 * for isomorphism testing. For more information, see
 * https://mivia.unisa.it/datasets/graph-database/arg-database/
 *
 * </para><para>
 * From the graph database homepage:
 * </para>
 *
 * \blockquote <para>
 * The graphs are stored in a compact binary format, one graph per
 * file. The file is composed of 16 bit words, which are represented
 * using the so-called little-endian convention, i.e. the least
 * significant byte of the word is stored first.</para>
 *
 * <para>
 * Then, for each node, the file contains the list of edges coming
 * out of the node itself. The list is represented by a word encoding
 * its length, followed by a word for each edge, representing the
 * destination node of the edge. Node numeration is 0-based, so the
 * first node of the graph has index 0.</para> \endblockquote
 *
 * <para>
 * As of igraph 0.10, only unlabelled graphs are implemented.
 *
 * \param graph Pointer to an uninitialized graph object.
 * \param instream The stream to read from. It should be opened
 *    in binary mode.
 * \param directed Logical scalar, whether to create a directed graph.
 * \return Error code.
 *
 * Time complexity: O(|V|+|E|), the number of vertices plus the
 * number of edges.
 *
 * \example examples/simple/igraph_read_graph_graphdb.c
 */
''',
"igraph_read_graph_graphml": '''
/**
 * \ingroup loadsave
 * \function igraph_read_graph_graphml
 * \brief Reads a graph from a GraphML file.
 *
 * </para><para>
 * GraphML is an XML-based file format for representing various types of
 * graphs. Currently only the most basic import functionality is implemented
 * in igraph: it can read GraphML files without nested graphs and hyperedges.
 * Attributes of the graph are loaded only if an attribute interface
 * is attached, see \ref igraph_set_attribute_table(). String attrribute values
 * are returned in UTF-8 encoding.
 *
 * </para><para>
 * Graph attribute names are taken from the <code>attr.name</code> attributes of the
 * \c key tags in the GraphML file. Since <code>attr.name</code> is not mandatory,
 * igraph will fall back to the \c id attribute of the \c key tag if
 * <code>attr.name</code> is missing.
 *
 * \param graph Pointer to an uninitialized graph object.
 * \param instream A stream, it should be readable.
 * \param index If the GraphML file contains more than one graph, the one
 *              specified by this index will be loaded. Indices start from
 *              zero, so supply zero here if your GraphML file contains only
 *              a single graph.
 *
 * \return Error code:
 *         \c IGRAPH_PARSEERROR: if there is a
 *         problem reading the file, or the file is syntactically
 *         incorrect.
 *         \c IGRAPH_UNIMPLEMENTED: the GraphML functionality was disabled
 *         at compile-time
 *
 * \example examples/simple/graphml.c
 */
''',
"igraph_read_graph_lgl": '''
/**
 * \ingroup loadsave
 * \function igraph_read_graph_lgl
 * \brief Reads a graph from an <code>.lgl</code> file.
 *
 * The <code>.lgl</code> format is used by the Large Graph
 * Layout visualization software
 * (http://lgl.sourceforge.net), it can
 * describe undirected optionally weighted graphs. From the LGL
 * manual:
 *
 * \blockquote <para>The second format is the LGL file format
 * (<code>.lgl</code> file
 * suffix). This is yet another graph file format that tries to be as
 * stingy as possible with space, yet keeping the edge file in a human
 * readable (not binary) format. The format itself is like the
 * following:
 * \verbatim # vertex1name
vertex2name [optionalWeight]
vertex3name [optionalWeight] \endverbatim
 * Here, the first vertex of an edge is preceded with a pound sign
 * '#'.  Then each vertex that shares an edge with that vertex is
 * listed one per line on subsequent lines.</para> \endblockquote
 *
 * </para><para>
 * LGL cannot handle loop and multiple edges or directed graphs, but
 * in \a igraph it is not an error to have multiple and loop edges.
 * \param graph Pointer to an uninitialized graph object.
 * \param instream A stream, it should be readable.
 * \param names Logical value, if \c true the symbolic names of the
 *        vertices will be added to the graph as a vertex attribute
 *        called \quote name\endquote.
 * \param weights Whether to add the weights of the edges to the
 *        graph as an edge attribute called \quote weight\endquote.
 *        \c IGRAPH_ADD_WEIGHTS_YES adds the weights (even if they
 *        are not present in the file, in this case they are assumed
 *        to be zero). \c IGRAPH_ADD_WEIGHTS_NO does not add any
 *        edge attribute. \c IGRAPH_ADD_WEIGHTS_IF_PRESENT adds the
 *        attribute if and only if there is at least one explicit
 *        edge weight in the input file.
 * \param directed Whether to create a directed graph. As this format
 *        was originally used only for undirected graphs there is no
 *        information in the file about the directedness of the graph.
 *        Set this parameter to \c IGRAPH_DIRECTED or \c
 *        IGRAPH_UNDIRECTED to create a directed or undirected graph.
 * \return Error code:
 *         \c IGRAPH_PARSEERROR: if there is a
 *         problem reading the file, or the file is syntactically
 *         incorrect.
 *
 * Time complexity:
 * O(|V|+|E|log(|V|)) if we neglect
 * the time required by the parsing. As usual
 * |V| is the number of vertices,
 * while |E| is the number of edges.
 *
 * \sa \ref igraph_read_graph_ncol(), \ref igraph_write_graph_lgl()
 *
 * \example examples/simple/igraph_read_graph_lgl.c
 */
''',
"igraph_read_graph_ncol": '''
/**
 * \ingroup loadsave
 * \function igraph_read_graph_ncol
 * \brief Reads an <code>.ncol</code> file used by LGL.
 *
 * Also useful for creating graphs from \quote named\endquote (and
 * optionally weighted) edge lists.
 *
 * </para><para>
 * This format is used by the Large Graph Layout program
 * (http://lgl.sourceforge.net), and it is simply a
 * symbolic weighted edge list. It is a simple text file with one edge
 * per line. An edge is defined by two symbolic vertex names separated
 * by whitespace. The vertex names themselves cannot contain
 * whitespace. They may be followed by an optional number,
 * the weight of the edge; the number can be negative and can be in
 * scientific notation. If there is no weight specified to an edge it
 * is assumed to be zero.
 *
 * </para><para>
 * The resulting graph is always undirected.
 * LGL cannot deal with files which contain multiple or loop edges,
 * this is however not checked here, as \a igraph is happy with
 * these.
 *
 * \param graph Pointer to an uninitialized graph object.
 * \param instream Pointer to a stream, it should be readable.
 * \param predefnames Pointer to the symbolic names of the vertices in
 *        the file. If \c NULL is given here then vertex IDs will be
 *        assigned to vertex names in the order of their appearance in
 *        the <code>.ncol</code> file. If it is not \c NULL and some unknown
 *        vertex names are found in the <code>.ncol</code> file then new vertex
 *        ids will be assigned to them.
 * \param names Logical value, if \c true the symbolic names of the
 *        vertices will be added to the graph as a vertex attribute
 *        called \quote name\endquote.
 * \param weights Whether to add the weights of the edges to the
 *        graph as an edge attribute called \quote weight\endquote.
 *        \c IGRAPH_ADD_WEIGHTS_YES adds the weights (even if they
 *        are not present in the file, in this case they are assumed
 *        to be zero). \c IGRAPH_ADD_WEIGHTS_NO does not add any
 *        edge attribute. \c IGRAPH_ADD_WEIGHTS_IF_PRESENT adds the
 *        attribute if and only if there is at least one explicit
 *        edge weight in the input file.
 * \param directed Whether to create a directed graph. As this format
 *        was originally used only for undirected graphs there is no
 *        information in the file about the directedness of the graph.
 *        Set this parameter to \c IGRAPH_DIRECTED or \c
 *        IGRAPH_UNDIRECTED to create a directed or undirected graph.
 * \return Error code:
 *         \c IGRAPH_PARSEERROR: if there is a
 *          problem reading
 *         the file, or the file is syntactically incorrect.
 *
 * Time complexity:
 * O(|V|+|E|log(|V|)) if we neglect
 * the time required by the parsing. As usual
 * |V| is the number of vertices,
 * while |E| is the number of edges.
 *
 * \sa \ref igraph_read_graph_lgl(), \ref igraph_write_graph_ncol()
 */
''',
"igraph_read_graph_pajek": '''
/**
 * \function igraph_read_graph_pajek
 * \brief Reads a file in Pajek format.
 *
 * \param graph Pointer to an uninitialized graph object.
 * \param file An already opened file handler.
 * \return Error code.
 *
 * </para><para>
 * Only a subset of the Pajek format is implemented. This is partially
 * because this format is not very well documented, but also because
 * <command>igraph</command> does not support some Pajek features, like
 * multigraphs.
 *
 * </para><para>
 * Starting from version 0.6.1 igraph reads bipartite (two-mode)
 * graphs from Pajek files and add the \c type vertex attribute for them.
 * Warnings are given for invalid edges, i.e. edges connecting
 * vertices of the same type.
 *
 * </para><para>
 * The list of the current limitations:
 * \olist
 * \oli Only <filename>.net</filename> files are supported, Pajek
 * project files (<filename>.paj</filename>) are not. These might be
 * supported in the future if there is need for it.
 * \oli Time events networks are not supported.
 * \oli Hypergraphs (i.e. graphs with non-binary edges) are not
 * supported.
 * \oli Graphs with both directed and non-directed edges are not
 * supported, are they cannot be represented in
 * <command>igraph</command>.
 * \oli Only Pajek networks are supported, permutations, hierarchies,
 * clusters and vectors are not.
 * \oli Graphs with multiple edge sets are not supported.
 * \endolist
 *
 * </para><para>
 * If there are attribute handlers installed,
 * <command>igraph</command> also reads the vertex and edge attributes
 * from the file. Most attributes are renamed to be more informative:
 * \c color instead of \c c, \c xfact instead of \c x_fact,
 * \c yfact instead of y_fact, \c labeldist instead of \c lr,
 * \c labeldegree2 instead of \c lphi, \c framewidth instead of \c bw,
 * \c fontsize
 * instead of \c fos, \c rotation instead of \c phi, \c radius instead
 * of \c r,
 * \c diamondratio instead of \c q, \c labeldegree instead of \c la,
 * \c vertexsize
 * instead of \c size, \c color instead of \c ic, \c framecolor instead of
 * \c bc, \c labelcolor instead of \c lc, these belong to vertices.
 *
 * </para><para>
 * Edge attributes are also renamed, \c s to \c arrowsize, \c w
 * to \c edgewidth, \c h1 to \c hook1, \c h2 to \c hook2,
 * \c a1 to \c angle1, \c a2 to \c angle2, \c k1 to
 * \c velocity1, \c k2 to \c velocity2, \c ap to \c
 * arrowpos, \c lp to \c labelpos, \c lr to
 * \c labelangle, \c lphi to \c labelangle2, \c la to \c
 * labeldegree, \c fos to
 * \c fontsize, \c a to \c arrowtype, \c p to \c
 * linepattern, \c l to \c label, \c lc to
 * \c labelcolor, \c c to \c color.
 *
 * </para><para>
 * In addition the following vertex attributes might be added: \c id
 * if there are vertex IDs in the file, \c x and \c y or \c x
 * and \c y and \c z if there are vertex coordinates in the file.
 *
 * </para><para>The \c weight edge attribute might be
 * added if there are edge weights present.
 *
 * </para><para>
 * See the pajek homepage:
 * http://vlado.fmf.uni-lj.si/pub/networks/pajek/ for more info on
 * Pajek and the Pajek manual:
 * http://vlado.fmf.uni-lj.si/pub/networks/pajek/doc/pajekman.pdf for
 * information on the Pajek file format.
 *
 * </para><para>
 * Time complexity: O(|V|+|E|+|A|), |V| is the number of vertices, |E|
 * the number of edges, |A| the number of attributes (vertex + edge)
 * in the graph if there are attribute handlers installed.
 *
 * \sa \ref igraph_write_graph_pajek() for writing Pajek files, \ref
 * igraph_read_graph_graphml() for reading GraphML files.
 *
 * \example examples/simple/foreign.c
 */
''',
	},
	"inchi": {
"GetINCHIKeyFromINCHI": '''
/*^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
GetINCHIKeyFromINCHI

Calculate InChIKey by InChI string.

Input:
        szINCHISource
            source InChI string
        xtra1
            =1 calculate hash extension (up to 256 bits; 1st block)
        xtra2
            =1 calculate hash extension (up to 256 bits; 2nd block)

Output:
        szINCHIKey
            InChIKey string
            The user-supplied buffer szINCHIKey should be at least 28 bytes long.
        szXtra1
            hash extension (up to 256 bits; 1st block) string
            Caller should allocate space for 64 characters + trailing NULL
        szXtra2
            hash extension (up to 256 bits; 2nd block) string
            Caller should allocate space for 64 characters + trailing NULL

Returns:
        success/errors codes

^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^*/
''',
"GetINCHIfromINCHI": '''
/*^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    GetINCHIfromINCHI

        GetINCHIfromINCHI does same as -InChI2InChI option: converts InChI into InChI for validation purposes
        It may also be used to filter out specific layers. For instance, /Snon would remove stereochemical layer
        Omitting /FixedH and/or /RecMet would remove Fixed-H or Reconnected layers
        To keep all InChI layers use options string "/FixedH /RecMet"; option /InChI2InChI is not needed
        inchi_InputINCHI is created by the user; strings in inchi_Output are allocated and deallocated by InChI
        inchi_Output does not need to be initilized out to zeroes; see FreeINCHI() on how to deallocate it

        Note: there is no explicit tool to conversion from/to standard InChI

    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^*/
''',
"GetStructFromINCHI": '''
/*^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    GetStructFromINCHI / GetStructFromStdINCHI / GetStructFromINCHIEx

        inchi_Inputinchi_InputINCHI is created by the user; pointers in inchi_OutputStruct are allocated and deallocated by InChI
        inchi_OutputStruct does not need to be initialized out to zeroes; see FreeStructFromStdINCHI() on how to deallocate it
        Option /Inchi2Struct is not needed for GetStructFromINCHI()/GetStructFromStdINCHI()

    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^*/
''',
	},
	"libmodbus": {
"modbus_read_bits": '''
/*
 * Description
 * The modbus_read_bits() function shall read the status of the nb bits (coils) to the address addr of the remote device. The result of reading is stored in dest array as unsigned bytes (8 bits) set to TRUE or FALSE.
 * 
 * You must take care to allocate enough memory to store the results in dest (at least nb * sizeof(uint8_t)).
 * 
 * The function uses the Modbus function code 0x01 (read coil status).
 * 
 * Return value
 * The function shall return the number of read bits if successful. Otherwise it shall return -1 and set errno.
 * 
 * Errors
 * EMBMDATA, too many bits requested
*/
''',
"modbus_read_registers": '''
/*
 * Description
 * The modbus_read_registers() function shall read the content of the nb holding registers to the address addr of the remote device. The result of reading is stored in dest array as word values (16 bits).
 * 
 * You must take care to allocate enough memory to store the results in dest (at least nb * sizeof(uint16_t)).
 * 
 * The function uses the Modbus function code 0x03 (read holding registers).
 * 
 * Return value
 * The function shall return the number of read registers if successful. Otherwise it shall return -1 and set errno.
 * 
 * Errors
 * EMBMDATA, too many registers requested.
*/
''',
"modbus_receive": '''
/*
 * Description
 * The modbus_receive() function shall receive an indication request from the socket of the context ctx. This function is used by a Modbus slave/server to receive and analyze indication request sent by the masters/clients.
 * 
 * If you need to use another socket or file descriptor than the one defined in the context ctx, see the function modbus_set_socket.
 * 
 * Return value
 * The function shall store the indication request in req and return the request length if successful. The returned request length can be zero if the indication request is ignored (eg. a query for another slave in RTU mode). Otherwise it shall return -1 and set errno.
 */
''',
	},
	"lua": {
"luaL_loadbufferx": '''
/*
 * Loads a buffer as a Lua chunk. This function uses lua_load to load the chunk in the buffer pointed to by buff with size sz.
 * 
 * This function returns the same results as lua_load. name is the chunk name, used for debug information and error messages. The string mode works as in function lua_load.
 */
''',
	},
	"md4c": {
"md_html": '''
/* Render Markdown into HTML.
 *
 * Note only contents of <body> tag is generated. Caller must generate
 * HTML header/footer manually before/after calling md_html().
 *
 * Params input and input_size specify the Markdown input.
 * Callback process_output() gets called with chunks of HTML output.
 * (Typical implementation may just output the bytes to a file or append to
 * some buffer).
 * Param userdata is just propagated back to process_output() callback.
 * Param parser_flags are flags from md4c.h propagated to md_parse().
 * Param render_flags is bitmask of MD_HTML_FLAG_xxxx.
 *
 * Returns -1 on error (if md_parse() fails.)
 * Returns 0 on success.
 */
''',
	},
	"oniguruma": {
"onig_new": '''
/*
 *  Create a regex object.
 *
 *  return value
 *  normal: ONIG_NORMAL == 0
 *  error:  error code < 0
 *
 *  arguments
 *  1 reg:         return regex object's address.
 *  2 pattern:     regex pattern string.
 *  3 pattern_end: terminate address of pattern. (pattern + pattern length)
 *  4 option:      compile time options.
 *
 *      ONIG_OPTION_NONE               no option
 *      ONIG_OPTION_SINGLELINE         '^' -> '\A', '$' -> '\Z'
 *      ONIG_OPTION_MULTILINE          '.' match with newline
 *      ONIG_OPTION_IGNORECASE         ambiguity match on
 *      ONIG_OPTION_EXTEND             extended pattern form
 *      ONIG_OPTION_FIND_LONGEST       find longest match
 *      ONIG_OPTION_FIND_NOT_EMPTY     ignore empty match
 *      ONIG_OPTION_NEGATE_SINGLELINE  clear ONIG_OPTION_SINGLELINE which is enabled on ONIG_SYNTAX_POSIX_BASIC/POSIX_EXTENDED/PERL/PERL_NG/PYTHON/JAVA
 *
 *      ONIG_OPTION_DONT_CAPTURE_GROUP only named group captured.
 *      ONIG_OPTION_CAPTURE_GROUP      named and no-named group captured.
 *
 *      ONIG_OPTION_IGNORECASE_IS_ASCII  Limit IGNORECASE((?i)) to a range of ASCII characters
 *      ONIG_OPTION_WORD_IS_ASCII      ASCII only word (\w, \p{Word}, [[:word:]])
 *                                     ASCII only word bound (\b)
 *      ONIG_OPTION_DIGIT_IS_ASCII     ASCII only digit (\d, \p{Digit}, [[:digit:]])
 *      ONIG_OPTION_SPACE_IS_ASCII     ASCII only space (\s, \p{Space}, [[:space:]])
 *      ONIG_OPTION_POSIX_IS_ASCII     ASCII only POSIX properties
 *                                     (includes word, digit, space)
 *                                     (alnum, alpha, blank, cntrl, digit, graph,
 *                                      lower, print, punct, space, upper, xdigit,
 *                                      word)
 *      ONIG_OPTION_TEXT_SEGMENT_EXTENDED_GRAPHEME_CLUSTER  Extended Grapheme Cluster mode
 *      ONIG_OPTION_TEXT_SEGMENT_WORD                       Word mode
 *
 *
 *     * The ONIG_OPTION_FIND_LONGEST option doesn't work properly during backward search of onig_search().
 *
 *
 *  5 enc:        character encoding.
 *
 *      ONIG_ENCODING_ASCII         ASCII
 *      ONIG_ENCODING_ISO_8859_1    ISO 8859-1
 *      ONIG_ENCODING_ISO_8859_2    ISO 8859-2
 *      ONIG_ENCODING_ISO_8859_3    ISO 8859-3
 *      ONIG_ENCODING_ISO_8859_4    ISO 8859-4
 *      ONIG_ENCODING_ISO_8859_5    ISO 8859-5
 *      ONIG_ENCODING_ISO_8859_6    ISO 8859-6
 *      ONIG_ENCODING_ISO_8859_7    ISO 8859-7
 *      ONIG_ENCODING_ISO_8859_8    ISO 8859-8
 *      ONIG_ENCODING_ISO_8859_9    ISO 8859-9
 *      ONIG_ENCODING_ISO_8859_10   ISO 8859-10
 *      ONIG_ENCODING_ISO_8859_11   ISO 8859-11
 *      ONIG_ENCODING_ISO_8859_13   ISO 8859-13
 *      ONIG_ENCODING_ISO_8859_14   ISO 8859-14
 *      ONIG_ENCODING_ISO_8859_15   ISO 8859-15
 *      ONIG_ENCODING_ISO_8859_16   ISO 8859-16
 *      ONIG_ENCODING_UTF8          UTF-8
 *      ONIG_ENCODING_UTF16_BE      UTF-16BE
 *      ONIG_ENCODING_UTF16_LE      UTF-16LE
 *      ONIG_ENCODING_UTF32_BE      UTF-32BE
 *      ONIG_ENCODING_UTF32_LE      UTF-32LE
 *      ONIG_ENCODING_EUC_JP        EUC-JP
 *      ONIG_ENCODING_EUC_TW        EUC-TW
 *      ONIG_ENCODING_EUC_KR        EUC-KR
 *      ONIG_ENCODING_EUC_CN        EUC-CN
 *      ONIG_ENCODING_SJIS          Shift_JIS
 *      ONIG_ENCODING_KOI8_R        KOI8-R
 *      ONIG_ENCODING_CP1251        CP1251
 *      ONIG_ENCODING_BIG5          Big5
 *      ONIG_ENCODING_GB18030       GB18030
 *
 *      or any OnigEncodingType data address defined by user.
 *
 *  6 syntax:     address of pattern syntax definition.
 *
 *      ONIG_SYNTAX_ASIS              plain text
 *      ONIG_SYNTAX_POSIX_BASIC       POSIX Basic RE
 *      ONIG_SYNTAX_POSIX_EXTENDED    POSIX Extended RE
 *      ONIG_SYNTAX_EMACS             Emacs
 *      ONIG_SYNTAX_GREP              grep
 *      ONIG_SYNTAX_GNU_REGEX         GNU regex
 *      ONIG_SYNTAX_JAVA              Java (Sun java.util.regex)
 *      ONIG_SYNTAX_PERL              Perl
 *      ONIG_SYNTAX_PERL_NG           Perl + named group
 *      ONIG_SYNTAX_PYTHON            Python
 *      ONIG_SYNTAX_ONIGURUMA         Oniguruma
 *      ONIG_SYNTAX_DEFAULT           default (== ONIG_SYNTAX_ONIGURUMA)
 *                                   onig_set_default_syntax()
 *
 *      or any OnigSyntaxType data address defined by user.
 *
 * 7 err_info: address for return optional error info.
 *            Use this value as 3rd argument of onig_error_code_to_str().
 */
''',
	},
}