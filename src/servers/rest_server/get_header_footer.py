import re, sys

# Create regular expressions that match the end of PGML / pg headers, and #
#     the beginning of PGML / pg footers                                  #

## Create regex to match header ends ##
header_ends = [
    r"BEGIN_TEXT",
    r"BEGIN_PGML",
    r"TEXT(PGML::Format2(<<'END_PGML'));",
    r"TEXT(PGML::Format2(<<'END_PGML'))"
]
escaped_header_ends = ["(%s)"%re.escape(header_end) 
    for header_end in header_ends]
header_end_regex = '|'.join(escaped_header_ends)

## Create regex to match footer beginnnings ##
footer_begins = [
    r"END_TEXT",
    r"END_PGML_SOLUTION",
    r"END_PGML"
]
escaped_footer_begins = ["(%s)"%re.escape(footer_begin) 
    for footer_begin in footer_begins]
footer_begin_regex =  '|'.join(escaped_footer_begins) 

def get_header(pg_file_str):
    ''' Get the header from a pg file: up to strings matched in "header_ends" '''
    try:
        header_end_index = re.finditer(header_end_regex, pg_file_str) \
            .next().start()
        return pg_file_str[:header_end_index]+"\nBEGIN_PGML\n"
    except StopIteration:
        return pg_file_str

def get_footer(pg_file_str):
    ''' Get the footer from a pg file: starting at strings matched in 
            "footer_begins" '''
    footer_begin = None
    for footer_begin in re.finditer(footer_begin_regex, pg_file_str):
        pass
    if footer_begin is None:
        return pg_file_str 
    else:
        return "\nEND_PGML\n"+pg_file_str[footer_begin.end():]

def title_str(title):
    return '#'*80 + '\n### %72s ###\n'%title + '#'*80

if __name__ == '__main__':
    with open(sys.argv[1], 'r') as f:
        pg_file_str = f.read()
    print title_str("Header Begin")
    print get_header(pg_file_str)
    print title_str("Header End")
    print title_str("Footer Begin")
    print get_footer(pg_file_str)
    print title_str("Footer End")
