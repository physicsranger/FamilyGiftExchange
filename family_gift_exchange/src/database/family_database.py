from sqlalchemy import (
    create_engine,
    select,
    update,
    delete,
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

###### Direct interface methods ######


    def add_or_update_family_member(self,
                                    name: str,
                                    email: str | None = None,
                                    address: str | None = None,
                                    significant_other: str | None = None):
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
        significant_other : str
            Name of the significant other of the family member whose record
            is being added or updated.  If the significant other has already
            been entered into the table, the name entered must exactly match.
            If the significant other is not in the table, they will be added
            with an alert to the user.
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

            # now we check if this member exists (updating) or if we are adding them
            member_info = {"name": name,
                           "email": email,
                           "address_id": address_id}
            
            if name in self.members(session):
                self._update_member(session, member_info)
            
            else:
                self._add_member(session, member_info)
            
            if significant_other is not None:
                self._update_significant_other(name,
                                               significant_other,
                                               address,
                                               session)
        
        # notify of success
        print(f"Successfully added/updated information for {name}.")
    
    def remove_family_member(self,
                             name: str):
        '''
        Method to remove a family member from the family table.  Note that
        this will not remove them from the history of name draws and it
        will not remove their address from the address table.  If the family
        member being removed had a significant other, that information will
        also be updated/deleted.

        Parameters
        ----------
        name : str
            The name of the family member to be removed.
        '''
        with self.Session.begin() as session:
            # check if the member is actually in the table
            if (member_id := self._get_member_id(name, session)) is None:
                print(f"{name} is not in the family table.")

            else:
                #first, make sure to update the corresponding significant other info
                so_id = self._get_so_id(name, session)
                if so_id is not None:
                    session.execute(update(SignificantOther, [{"id": so_id, "so_id": None}]))
                    session.execute(delete(SignificantOther).where(id=member_id))

                # now, remove the family member
                session.execute(delete(Family).where(name=name))
        
        print(f"{name} successfully removed from family table. "
               "Corresponding information in the significant_other table also removed.")


    def get_email(self,
                  name: str) -> str:
        '''
        Method to retrieve the email address for a given family member

        Parameters
        ----------
        name : str
            The name of the family member whose email address is requested.

        Returns
        -------
        str or NoneType
            The email for the requested family member, might be a NoneType
            if no email address was entered in the database.
        
        Raises
        ------
        KeyError
            If the requested family member is not found in the database,
            raise an error.
        '''

        with self.Session() as session:
            # first, check if the family member is in the database
            if name not in self.members(session):
                raise KeyError(f"{name} not found in family table.")
            
            email = session.execute(
                select(Family.email).filter_by(name=name)
            ).first()[0]
        
        return email
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
        Method to get the so_id value of the significant
        other of the specified family member (by name).

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


    def _update_significant_other(self,
                                 member1: str,
                                 member2: str,
                                 session: Session,
                                 address: str | None = None):
        '''
        Method to  update the significant_other table, connecting
        family members via id values.  If either of the two members
        is not in the table, they will be added.  An optional address
        string can be included.

        Parameters
        ----------
        member1 : str
            The name of one family member for which significant other info
            will be updated.
        member2 : str
            The name of a second family member for which significant other
            info will be updated.
        session : sqlalchemy.orm.Session
            The current database connection.
        address : str or NoneType
            An address string which will be used if either member is not
            in the database, the same address is used for both.
        '''
        # get the address id
        # use _add_address since it will check if the address exists
        # return if it does and add if it doesn't
        address_id = self._add_address(address, session)

        # get the member_id values
        member_ids = []
        for member in [member1, member2]:
            if member not in self.members(session):
                print(f"Updating significant other information, did not find {member}, "
                      f"will be added with address string {address}")
                self._add_member(session, {"name": member, "address_id": address_id})
            
            member_ids.append(self._get_member_id(member1, session))

        # now update the table
        session.execute(
            update(SignificantOther, [{"id": member_ids[0], "so_id": member_ids[1]},
                                      {"id": member_ids[1], "so_id": member_ids[0]}])
        )
