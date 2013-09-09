''' Once we've run the command show_mysql_summaries.sql against the webwork
        database
    '''

out_file = 'out.csv' #The file containing the output of running the show_mysql_summaries.sql 
    # command.  The mysql output should be in .csv format
course = 'UCSD_CSE103_' #Tables output frpom show_mysql_summaries are of the form
    # <course>...

tables = []

def add_table_info(table, schema, first_row):
    ''' If the table has at least one row, then the table/schema/first row
        should be in the csv file.  In this case, append to tables.  
        '''
    if all((not x is None for x in [table, schema, first_row] )):
        tables.append( (table, schema, first_row))

# Process the csv file into a list tables of the form:
#  (table, schema, first_row)
table, schema, first_row = [None]*3
with open(out_file,'r') as f:
    for line in f.readlines():
        if len(line.strip()) == 0:
            add_table_info(table, schema, first_row)
            table, schema, first_row = [None]*3
            i = 0
        if i == 1:
            table = line.strip()
        elif i == 2:
            schema = line.strip()
        elif i == 3:
            first_row = line.strip()
        i += 1

# Map each table into a column/first row value dictionary
table_dict = {}
for table, schema, first_row in tables:
    if course in table:
        table = table.replace(course,'')
        description = {}
        for column, val in zip(schema.split('\t'), first_row.split('\t')):
            description[column] = {"first_row":val, "description":""}
        table_dict[table] = description

if __name__ == '__main__':
    # Pretty print to markdown
    for table, cols in table_dict.iteritems():
        print '# %s #'%table
        for col, v in cols.iteritems():
            val = v["first_row"]
            print '### %s ###'%col
            if val.strip() != 'NULL':
                print '* Example: %s'%val
#            print '* Description: '
        print '\n'
