"""Definition of meta model 'legacy_library'."""
from functools import partial
import pyecore.ecore as Ecore
from pyecore.ecore import *


name = 'legacy_library'
nsURI = 'http://emf.wikipedia.org/2011/Library'
nsPrefix = 'lib'

eClass = EPackage(name=name, nsURI=nsURI, nsPrefix=nsPrefix)

eClassifiers = {}
getEClassifier = partial(Ecore.getEClassifier, searchspace=eClassifiers)
BookCategory = EEnum('BookCategory', literals=['ScienceFiction', 'Biographie', 'Mistery'])


class Employee(EObject, metaclass=MetaEClass):

    name = EAttribute(eType=EString, unique=True, derived=False, changeable=True)
    age = EAttribute(eType=EInt, unique=True, derived=False, changeable=True, default_value=0)

    def __init__(self, *, name=None, age=None):
        # if kwargs:
        #    raise AttributeError('unexpected arguments: {}'.format(kwargs))

        super().__init__()

        if name is not None:
            self.name = name

        if age is not None:
            self.age = age


class DerivedAges(EDerivedCollection):
    pass


class DerivedMorethan20(EDerivedCollection):
    pass


class Library(EObject, metaclass=MetaEClass):
    """Top-level object for library management."""
    ages = EAttribute(eType=EInt, unique=True, derived=True, changeable=True,
                      upper=-1, transient=True, derived_class=DerivedAges)
    name = EAttribute(eType=EString, unique=True, derived=False, changeable=True)
    address = EAttribute(eType=EString, unique=True, derived=False, changeable=True)
    employees = EReference(ordered=True, unique=True, containment=True, derived=False, upper=-1)
    writers = EReference(ordered=True, unique=True, containment=True, derived=False, upper=-1)
    books = EReference(ordered=True, unique=True, containment=True, derived=False, upper=-1)
    moreThan20 = EReference(ordered=True, unique=True, containment=True,
                            derived=True, upper=-1, transient=True, derived_class=DerivedMorethan20)

    def __init__(self, *, ages=None, name=None, address=None, employees=None, writers=None, books=None, moreThan20=None):
        # if kwargs:
        #    raise AttributeError('unexpected arguments: {}'.format(kwargs))

        super().__init__()

        if ages:
            self.ages.extend(ages)

        if name is not None:
            self.name = name

        if address is not None:
            self.address = address

        if employees:
            self.employees.extend(employees)

        if writers:
            self.writers.extend(writers)

        if books:
            self.books.extend(books)

        if moreThan20:
            self.moreThan20.extend(moreThan20)


class Writer(EObject, metaclass=MetaEClass):

    name = EAttribute(eType=EString, unique=True, derived=False, changeable=True)
    books = EReference(ordered=True, unique=True, containment=False, derived=False, upper=-1)

    def __init__(self, *, name=None, books=None):
        # if kwargs:
        #    raise AttributeError('unexpected arguments: {}'.format(kwargs))

        super().__init__()

        if name is not None:
            self.name = name

        if books:
            self.books.extend(books)


class Book(EObject, metaclass=MetaEClass):

    title = EAttribute(eType=EString, unique=True, derived=False, changeable=True)
    pages = EAttribute(eType=EInt, unique=True, derived=False, changeable=True, default_value=0)
    category = EAttribute(eType=BookCategory, unique=True, derived=False,
                          changeable=True, default_value=BookCategory.ScienceFiction)
    authors = EReference(ordered=True, unique=True, containment=False, derived=False, upper=-1)

    def __init__(self, *, title=None, pages=None, category=None, authors=None):
        # if kwargs:
        #    raise AttributeError('unexpected arguments: {}'.format(kwargs))

        super().__init__()

        if title is not None:
            self.title = title

        if pages is not None:
            self.pages = pages

        if category is not None:
            self.category = category

        if authors:
            self.authors.extend(authors)
