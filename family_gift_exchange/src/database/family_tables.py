from sqlalchemy import (
    String,
    ForeignKey)

from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship)

class Base(DeclarativeBase):
    pass

class Family(Base):
    __tablename__ = 'family'

    #figure out autoincrement
    id: Mapped[int] = mapped_column(primary_key = True)
    name: Mapped[str] = mapped_column(String(64), nullable = False)
    email: Mapped[str] = mapped_column(String(128), nullable = True)
    address_id: Mapped[int] = mapped_column(ForeignKey('address.id'))

    address_table: Mapped['Address'] = relationship(back_populates = 'family')
    so_table: Mapped['SignificantOther'] = relationship(back_populates = 'family')
    exchange: Mapped['Exchange'] = relationship(back_populates = 'family')

    def __repr__(self) -> str:
        return f'{self.name}, email: {self.email}'

class Address(Base):
    __tablename__ = 'address'

    #figure out autoincrement
    id: Mapped[int] = mapped_column(primary_key = True)
    address: Mapped[str] = mapped_column(String(256), nullable = True)

    family_table: Mapped[Family] = relationship(back_populates = 'address')

    def __repr__(self) -> str:
        return f'{self.id}: {self.address}'

class SignificantOther(Base):
    __tablename__ = 'significant_other'

    id: Mapped[int] = mapped_column(ForeignKey('family.id'), primary_key = True)
    so_id: Mapped[int] = mapped_column(nullable = True)

    family_table: Mapped[Family] = relationship(back_populates = 'significant_other')

    def __repr__(self) -> str:
        return f'id = {self.id} -> so = {self.so_id}'

#this is where things get interesting since
# previously kept adding columns to the table
#let's try a multi-column primary key
#and add a new draw column, which may be nullable,
#so we'll need to account for and catch instances
#where the draw id no longer exists
class Exchange(Base):
    __tablename__ = 'exchange'

    id: Mapped[int] = mapped_column(ForeignKey('family.id'), primary_key = True)
    year: Mapped[int] = mapped_column(primary_key = True)
    draw_id: Mapped[int] = mapped_column(nullable = True)

    family_table: Mapped[Family] = relationship(back_populates = 'exchange')

    def __repr__(self) -> str:
        return (f'For year {self.year}, family member {self.id} '
                f'drew family member {self.draw_id}')
