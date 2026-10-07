
from .legacy_library import getEClassifier, eClassifiers
from .legacy_library import name, nsURI, nsPrefix, eClass
from .legacy_library import Employee, Library, Writer, Book, BookCategory


from . import legacy_library

__all__ = ['Employee', 'Library', 'Writer', 'Book', 'BookCategory']

eSubpackages = []
eSuperPackage = None
legacy_library.eSubpackages = eSubpackages
legacy_library.eSuperPackage = eSuperPackage

Library.employees.eType = Employee
Library.writers.eType = Writer
Library.books.eType = Book
Library.moreThan20.eType = Employee
Writer.books.eType = Book
Book.authors.eType = Writer
Book.authors.eOpposite = Writer.books

otherClassifiers = [BookCategory]

for classif in otherClassifiers:
    eClassifiers[classif.name] = classif
    classif.ePackage = eClass

for classif in eClassifiers.values():
    eClass.eClassifiers.append(classif.eClass)

for subpack in eSubpackages:
    eClass.eSubpackages.append(subpack.eClass)
