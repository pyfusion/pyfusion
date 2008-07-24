import pyfusion

def ftplot(signal, shot, yrange=[False, False], xrange=[False, False], ytype=1, window=False, time_segment=0.001):
    pass


def new_show_db(partial_name='', page_width=80):
    """ frozen native SQLAlchemy version - see utils.py for latest
    Works on all databases, f.metadata.tables is probably a very indirect way to
    access data
    """
    tmp = pyfusion.session.query(pyfusion.Device)
    f=tmp.first()
    table_list = f.metadata.tables.values()
    counts=[] ; table_names=[]
    for (i,table) in enumerate(table_list):    
        table_name=str(table)
        countqry=table.count()
        count=countqry.execute().fetchone()[0]
        counts.append(count) ; table_names.append(table_name)

    len_wid = max([len(str(st)) for st in counts])
    tabl_wid = max([len(st) for st in table_names])
    for (i,table) in enumerate(table_list):    
        # print str(table), count, str(table._columns)
        col_list_long =  str(table._columns)
        col_list= [ss.strip("' ") for ss in col_list_long.strip("[]").split(",")]
        col_list_short= [ss.replace(table_names[i]+'.','') for ss in col_list]
        print ('%*s:[%*s] ') % ( tabl_wid,table_names[i],len_wid,counts[i]),
        start_col=len_wid+tabl_wid+6
        next_col=start_col
        for (i,strg) in enumerate(col_list_short): 
            if (next_col+len(strg)+2 > page_width): 
                print 
                print('%*s') % (start_col,""),
                next_col=start_col
            print ('%s,') % (strg),
            next_col += len(strg)+2
        print 

def show_db(db="", extra = "", page_width=80):
    """
    Brief description of database, only  works in mysql - maybe there is a fancy sqlalchemy version
    Note that the database does NOT default to the one defined in pyfusion.settings
    Would be nice to indicate strings by quotes and blobs by *  e.g.  example: id, "name", *image
    """
    import sqlalchemy
    from numpy import transpose
    from sqlalchemy import create_engine

# could be an independent module if this line was removed....
# but then how would we do the test?
# maybe default to the db name parsed from SQL_SERVER
# This would require a pyfusion.show_db, that called the general show_db - nice!
    # 
    if (db=="") and (pyfusion.settings.SQL_SERVER.upper().find('MYSQL') < 0): 
        raise Exception, ' only for mysql databases'
    
    engine = create_engine('mysql://localhost/information_schema')
    conn = engine.connect()

    from sqlalchemy.sql import text

#    s = text("SELECT c.table_name,c.column_name,t.table_rows from columns as c, tables as t where c.TABLE_SCHEMA = '" 
#             + db + "' and t.TABLE_SCHEMA = '" + db + "' "+extra)

    tabsel = text("SELECT table_name,table_rows from tables where TABLE_SCHEMA = '" + db + "' "+extra)

    result=conn.execute(tabsel).fetchall()
    tr = transpose(result)
    table_arr = tr[0,:]
    length_arr = tr[1,:]
    len_wid = max([len(st) for st in length_arr])
    name_wid = max([len(st) for st in table_arr])
    for (i,strg) in enumerate(table_arr): 
        print ('%*s:[%*s] ') % ( name_wid,strg,len_wid,length_arr[i]),
        colsel = text("SELECT column_name from columns where table_name='"+ strg +"' and TABLE_SCHEMA = '" + db + "' "+extra)
        result=conn.execute(colsel).fetchall()
        trc = transpose(result)
        col_arr = trc[0,:]
        start_col=len_wid+name_wid+6
        next_col=start_col
        for (i,strg) in enumerate(col_arr): 
            if (next_col+len(strg)+2 > page_width): 
                print 
                print('%*s') % (start_col,""),
                next_col=start_col
            print ('%s,') % (strg),
            next_col += len(strg)+2
        print 
