"""
Academic models aggregate module.
Re-exports Semester, AcademicSession, and ClassDivision for convenient importing.
"""
from app.models.semester import Semester
from app.models.academic_session import AcademicSession
from app.models.class_division import ClassDivision

__all__ = ['Semester', 'AcademicSession', 'ClassDivision']
