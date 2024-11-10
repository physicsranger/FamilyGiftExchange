from sqlalchemy import (
    create_engine,
    select,
    update
)
from sqlalchemy.exc import IntegrityError

from sqlalchemy.orm import sessionmaker

from sqlalchemy.orm.exc import StaleDataError

from .family_tables import (
    Base,
    Family,
    Address,
    SignificantOther,
    Exchange)

from pathlib import Path
from typing import Any

class MyFamily:
    def __init__(self,
                 db_file: str|Path,
                 echo: bool = False):
        self.db_file = Path(db_file)
        self.db_url = fr'sqlite:///{db_file}'
        self.echo = echo

        self.engine = create_engine(self.db_url, echo = self.echo)

        if not self.db_file.exists():
            Base.metadata.create_all(self.engine)
        
        self.Session = sessionmaker(self.engine)
    
    def __repr__(self) -> str:
        return f'Database at {self.db_url}, with option echo = {self.echo}'
    
    #to match current functionality, want methods to
    #add family member
    #update family member info
    #add new address
    ##these will include sub-methods to add/change address
    ## assigned to a family member
    ##add/change significant other
    #remove a family member
    #do we need the "count_at_address" functionality?
    #similar to serials property, property to get all member names

    @property
    def members(self) -> set[str|None]:
        '''gett for members attribute which will
        return a set of all family member names in
        the current family table

        Returns
        -------
        set (str)
            all 'name' values from the family table
        '''

        with self.Session() as session:
            members = session.scalars(select(Family.name)).all()
        
        return set(members)
    
    @property
    def member_ids(self) -> dict:
        '''
        property to access a dictionary with
        family member names as keys and family
        table id number as values
        '''

        with self.Session() as session:
            members = session.scalars(select(Family.id, Family.name)).all()
        
        return {member.name: member.id for member in members}

    def add_or_update_family_member(self,
                                    name: str,
                                    **kwargs: Any):

        with self.Session.begin() as session:
            if name in self.members:
                #updating
                #probably need try/except for if address_id is
                #specified and not in address table (IntegrityError?)
                session.execute(update(Family, [kwargs]))

            else:
                #adding new member
                #make sure not to try and specify
                #id just in case it was passed in
                kwargs.update([('id', None)])
                session.add(Family(name = name, **kwargs))
    
    def remove_family_member(self,
                             name: str):
        pass

    def add_update_significant_other(self,
                                     name: str,
                                     so_name: str):
        #look up name in family to get id
        #look up so_name in family to get id to map to so_id
        #need to catch error when one name doesn't exist
        pass




    