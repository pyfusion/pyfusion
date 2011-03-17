"""Object relational mapping for Pyfusion"""

import pyfusion
"""
if pyfusion.USE_ORM:
    import sqlalchemy

def setup_orm():
    from sqlalchemy import create_engine, MetaData
    from sqlalchemy.orm import scoped_session, sessionmaker

    pyfusion.orm_engine = create_engine(pyfusion.config.get('global', 'database'))
    pyfusion.Session = scoped_session(sessionmaker(autocommit=False,
                                                   autoflush=True,
                                                   bind=pyfusion.orm_engine,
                                                   expire_on_commit=False))
    if not hasattr(pyfusion, 'metadata'):
        pyfusion.metadata = MetaData()
    pyfusion.metadata.bind = pyfusion.orm_engine
    pyfusion.metadata.create_all()


def takedown_orm():
    del pyfusion.metadata
    del pyfusion.Session
    del pyfusion.orm_engine


"""
class ORMManager(object):
    def __init__(self):
        self.func_list = []
        self.IS_ACTIVE = False
    def add_reg_func(self, orm_func):
        self.func_list.append(orm_func)

    def setup_session(self):
        db_string = pyfusion.config.get('global', 'database')

        if db_string.lower() != 'none':
            from sqlalchemy import create_engine, MetaData
            from sqlalchemy.orm import scoped_session, sessionmaker, clear_mappers
        
            self.engine = create_engine(pyfusion.config.get('global', 'database'))
            self.Session = scoped_session(sessionmaker(autocommit=False,
                                                       autoflush=True,
                                                       bind=self.engine,
                                                       expire_on_commit=False))
        
            self.metadata = MetaData()
            self.metadata.bind = self.engine
            self.metadata.create_all()
        
            self.IS_ACTIVE = True

            # for use in tests
            self.clear_mappers = clear_mappers


    def load_orm(self):
        self.setup_session()
        for f in self.func_list:
            f(self)
        self.metadata.create_all()

    def shutdown_orm(self):
        #TODO:...
        pass
    
