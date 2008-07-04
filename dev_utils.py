def ftplot(signal, shot, yrange=[False, False], xrange=[False, False], ytype=1, window=False, time_segment=0.001):
    pass


def show_db(db = 'pyfusion', extra = ""):
    import sqlalchemy
    from numpy import transpose
    from sqlalchemy import create_engine

    engine = create_engine('mysql://localhost/information_schema')
    conn = engine.connect()

    from sqlalchemy.sql import text

    s = text("SELECT c.table_name,c.column_name,t.table_rows from columns as c, tables as t where c.TABLE_SCHEMA = '" + db + "' and t.TABLE_SCHEMA = '" + db + "' "+extra)

    tabsel = text("SELECT table_name,table_rows from tables where TABLE_SCHEMA = '" + db + "' "+extra)

    result=conn.execute(tabsel).fetchall()
    tr = transpose(result)
    table_arr = tr[0,:]
    length_arr = tr[1,:]
    for (i,str) in enumerate(table_arr): 
        print ('%5s: %s: ') % (length_arr[i], str,),
        colsel = text("SELECT column_name from columns where table_name='"+ str +"' and TABLE_SCHEMA = '" + db + "' "+extra)
        result=conn.execute(colsel).fetchall()
        trc = transpose(result)
        col_arr = trc[0,:]
        for (i,str) in enumerate(col_arr): print ('%s,') % (str),
        print 
