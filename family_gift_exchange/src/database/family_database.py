from sqlalchemy import (
    create_engine,
    select,
    update
)
from sqlalchemy.exc import IntegrityError

from sqlalchemy.orm import (
    sessionmaker,
    Session,   
)

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

    def members(self,
                session: Session) -> set[str|None]:
        '''
        function to return a set of all family member names in
        the current family table

        Parameters
        ----------
        session : sqlalchemy.orm.Session
            the current database connection session

        Returns
        -------
        set (str)
            all 'name' values from the family table
        '''

        members = session.scalars(select(Family.name)).all()
        
        return set(members)
    

    def member_ids(self,
                   session: Session) -> dict:
        '''
        functionto create a dictionary with
        family member names as keys and family
        table id number as values

        Parameters
        ----------
        session : sqlalchemy.orm.Session
            the current database connections session

        Returns
        -------
        dict
            a dictionary with (key, value) pairs of
            (name, id)
        '''

        members = session.scalars(select(Family.id, Family.name)).all()
        
        return {member.name: member.id for member in members}

    # conundrum, we could pass in a "session" (optional None) to better
    # match the suggested best practices; however, there won't be significant
    # changes between access given the limited nature of this particular database
    # so, for now, we will leave this thought here but proceed as we have been
    def add_or_update_family_member(self,
                                    name: str,
                                    email: str | None = None,
                                    address: str | None = None,
                                    significant_other : str | None = None):
        '''
        function to add or update information about a family member
        '''

        # first, we'll connect to the database
        with self.Session.begin() as session:
            # now check if the address already exists
            if address is not None:
                address_id = self._get_address_id(address, session)
                
                # if we didn't find anything, insert the address
                # and get the id
                if address_id is None:
                    address_id = self._add_address(address, session)
            
            else:
                address_id = None
            
            # check if the significant_other is in the database
            # get their so_id if they are
            if significant_other is not None:
                if significant_other in self.members(session):
                    so_id = self._get_member_id(significant_other, session)
                
                else:
                    print(f"Significant other ({significant_other}) specified for "
                          f"{name} but not in family table.  Will add {significant_other}, "
                          "assuming same address, if specified, you may need to manually "
                          "update or correct this information.")
                    
                    so_id = self._add_member(session,
                                            {"name": significant_other,
                                             "address_id": address})
            
            else:
                so_id = None


    def _get_address_id(self,
                        address: str,
                        session: Session) -> int | None:
        
        address_id = session.execute(
            select(Address.id).filter_by(address=address)
                ).first()[0]
        
        return address_id

    def _add_address(self,
                     address: str,
                     session: Session) -> int:
        # try to add the new address
        try:
            session.add(Address(address=address))
        
        except IntegrityError:
            # catch the error to reraise it but with our message
            raise IntegrityError(f"Cannot add {address}, already in the table.")

        # return the new id
        return self._get_address_id(address, session)

    def _get_so_id(self,
                   significant_other: str,
                   session: Session) -> int | None:
        
        member_id = session.execute(
            select(Family.id).filter_by(name=significant_other)
        )

        if member_id is None:
            return None

        so_id = session.execute(
            select(SignificantOther.so_id).filter_by(id=member_id)
        )

        return so_id
    
    def _get_member_id(self,
                       name: str,
                       session: Session) -> int:
        
        member_id = session.execute(
            select(Family.id).filter_by(name=name)
        ).first()[0]

        return member_id

    def _add_member(self,
                     session: Session,
                     **kwargs) -> int:
        '''
        Function to actual interface with the database via a session
        '''
        # first, make sure someone didn't try to pass the id value in
        try:
            _ = kwargs.pop('id')
            print("Warning, the id parameter should not be specified, removing.")

        except KeyError:
            pass

        # now check that the name parameter has been added
        # other wise the add command will fail
        if 'name' not in kwargs.keys():
            raise KeyError("User must specify a name for new family member. "
                           f"Key 'name' not found among inputs: {kwargs.keys()}")

        # now, add the new family member
        session.add(Family(**kwargs))

        # and return the new id
        member_id = self._get_member_id(kwargs.get("name"), session)

        return member_id

        # with self.Session.begin() as session:
            # session.execute(statement)
            # if name in self.members:
            #     #updating
            #     #probably need try/except for if address_id is
            #     #specified and not in address table (IntegrityError?)
            #     session.execute(update(Family, [kwargs]))

            # else:
            #     #adding new member
            #     #make sure not to try and specify
            #     #id just in case it was passed in
            #     try:
            #         _ = kwargs.pop('id')
            #     except KeyError:
            #         pass

            #     session.add(Family(name = name, **kwargs))
    
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




    