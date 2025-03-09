from sqlalchemy import (
    create_engine,
    select,
    update
)

from sqlalchemy.orm import (
    sessionmaker,
    Session,   
)

from sqlalchemy.orm.exc import StaleDataError
from sqlalchemy.exc import IntegrityError

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
        Method to return a set of all family member names in
        the current family table

        Parameters
        ----------
        session : sqlalchemy.orm.Session
            The current database connection.

        Returns
        -------
        set (str)
            A set of all 'name' values from the family table.
        '''

        members = session.scalars(select(Family.name)).all()
        
        return set(members)
    
    # likely going to delete this method
    # def member_ids(self,
    #                session: Session) -> dict:
    #     '''
    #     functionto create a dictionary with
    #     family member names as keys and family
    #     table id number as values

    #     Parameters
    #     ----------
    #     session : sqlalchemy.orm.Session
    #         the current database connections session

    #     Returns
    #     -------
    #     dict
    #         a dictionary with (key, value) pairs of
    #         (name, id)
    #     '''

    #     members = session.scalars(select(Family.id, Family.name)).all()
        
    #     return {member.name: member.id for member in members}


    def add_or_update_family_member(self,
                                    name: str,
                                    email: str | None = None,
                                    address: str | None = None):
        '''
        Method to add or update information about a family member.

        Parameters
        ----------
        name : str
            Name of the family member for which information should be
            added/updated.
        email : str
            Optional email address for this family member.
        address : str
            Optional address for this family member, should be entered with
            new line characters separating the elements - address line 1,
            address line 2 (blank if not applicable), city, state, zip code,
            and country.  This is automatically handled by the GUI.
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
            
            # # check if the significant_other is in the database
            # # get their so_id if they are
            # if significant_other is not None:
            #     if significant_other in self.members(session):
            #         so_id = self._get_member_id(significant_other, session)
                
            #     else:
            #         print(f"Significant other ({significant_other}) specified for "
            #               f"{name} but not in family table.  Will add {significant_other}, "
            #               "assuming same address, if specified, you may need to manually "
            #               "update or correct this information.")
                    
            #         so_id = self._add_member(session,
            #                                 {"name": significant_other,
            #                                  "address_id": address})
            
            # else:
            #     so_id = None

            # now we check if this member exists (updating) or if we are adding them
            member_info = {"name": name,
                           "email": email,
                           "address_id": address_id}
            
            if name in self.members(session):
                self._update_member(session, member_info)
            
            else:
                self._add_member(session, member_info)
            
            # if significant_other is not None:
            #     _ = self._update_member(session,
            #                             {"id": so_id,
            #                              "name": significant_other,
            #                              "so_id": member_id})
        
        # notify of success
        print(f"Successfully added/updated information for {name}.")
    
    def remove_family_member(self,
                             name: str):
        pass


    def update_significant_other(self,
                                 name: str,
                                 significant_other: str):
        pass

##### methods only expected to be called by other object methods #####
    def _get_address_id(self,
                        address: str,
                        session: Session) -> int | None:
        '''
        Method to return the id column from the address
        table corresponding to the input address string

        Parameters
        ----------
        address : str
            The address string, formatted to havenew line characters separating
            the elements - address line 1, address line 2 (blank if not applicable),
            city, state, zip code, and country. This is automatically handled by the GUI.
        
        session : sqlalchemy.orm.Session
            The current database connection
        
        Returns
        -------
        int or NoneType
            The address table id column matching the input address string or a 
            NoneType if there is no match
        '''
        
        address_id = session.execute(
            select(Address.id).filter_by(address=address)
                ).first()[0]
        
        return address_id

    def _add_address(self,
                     address: str,
                     session: Session) -> int:
        '''
        Method to an a new address string to the address table.

        Parameters
        ----------
        address : str
            The address string, formatted to havenew line characters separating
            the elements - address line 1, address line 2 (blank if not applicable),
            city, state, zip code, and country. This is automatically handled by the GUI.
        
        session : sqlalchemy.orm.Session
            The current database connection
        
        Returns
        -------
        int
            The value of the id column for the newly added for in the address table.
        
        Raises
        ------
        IntegrityError
            If trying to add an address that already exists, raise an error.
        '''
        # only add the address if it isn't in there
        while (address_id := self._get_address_id(address, session)) is None:
            # try to add the new address
            try:
                session.add(Address(address=address))
        
            except IntegrityError as error:
                # catch the error to reraise it but with our message
                # shouldn't happen if we aren't specifying the id
                raise IntegrityError(f"Cannot add address = {address}.\n"
                                 f"Exception info: {error}")

        # return the id
        return address_id

    def _get_so_id(self,
                   name: str,
                   session: Session) -> int | None:
        '''
        Method to get the id value of the specified
        family member (by name).

        Parameters
        ----------
        name : str
            Name of the family member for which you want to
            get the id of their significant other
        session : sqlalchemy.orm.Session
            The current database connect.
        
        Returns
        -------
        int or NoneType
            The id of the specified family member's significant
            other, if they have one, otherwise return NoneType.
        '''
        member_id = session.execute(
            select(Family.id).filter_by(name=name)
        ).first[0]

        if member_id is None:
            return None

        so_id = session.execute(
            select(SignificantOther.so_id).filter_by(id=member_id)
        )

        return so_id
    
    def _get_member_id(self,
                       name: str,
                       session: Session) -> int | None:
        '''
        Method to get the id of a given family member.

        Parameters
        ----------
        name : str
            The name of the family member of interest
        session : sqlalchemy.orm.Session
            The current database connection.
        
        Returns
        -------
        int or NoneType
            The id value of the specified family member.
            If no name match is found, returned value will
            be a NoneType.
        '''
        member_id = session.execute(
            select(Family.id).filter_by(name=name)
        ).first()[0]

        return member_id

    def _add_member(self,
                     session: Session,
                     **kwargs):
        '''
        Method to add a new family member to the family table.

        Parameters
        ----------
        session : sqlalchemy.orm.Session
            The current database connection.
        kwargs : dict[various]
            Values to be added to the family table, must have a
            "name" key.  If this dict includes a key "id", that
            will be removed.
        
        Raises
        ------
        KeyError
            If no name is specified for the family member, raise an error.
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

    
    def _update_member(self,
                       session: Session,
                       **kwargs):
        '''
        Method to update the information for a given
        entry in the family table.

        Parameters
        ----------
        session : sqlalchemy.orm.Session
            The current database connection.
        kwargs : dict[various]
            The values needed to identify the row to update as
            well as the values to update.

        Raises
        ------
        StaleDataError
            If the information cannot be updated, raise an error.
        '''
        # likely need some sort of try-except block
        try:
            session.execute(update(Family, [kwargs]))
        
        except StaleDataError as error:
            # catch the exception to reraise with our info
            raise StaleDataError("Could not update information for family member "
                                f"with name '{kwargs.get('name')}' (id {kwargs.get('id')}).\n"
                                f"Exception info: {error}")




    