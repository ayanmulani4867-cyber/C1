from flask import abort
from flask_login import current_user


def check_student_access(student):
    """
    Ensure only Admin, HOD of the student's department, or the student themselves can access their data.
    """
    if not current_user.is_authenticated:
        abort(403)
    
    if current_user.is_admin:
        return True
    
    if current_user.is_hod:
        hod_faculty = current_user.faculty_profile
        if hod_faculty and hod_faculty.department_id == student.department_id:
            return True
        abort(403)
        
    if current_user.is_student:
        if current_user.student_profile and current_user.student_profile.id == student.id:
            return True
        abort(403)
        
    abort(403)


def check_faculty_access(faculty):
    """
    Ensure only Admin, HOD of the faculty's department, or the faculty themselves can access.
    """
    if not current_user.is_authenticated:
        abort(403)
        
    if current_user.is_admin:
        return True
        
    if current_user.is_hod:
        hod_faculty = current_user.faculty_profile
        if hod_faculty and hod_faculty.department_id == faculty.department_id:
            return True
        abort(403)
        
    if current_user.faculty_profile and current_user.faculty_profile.id == faculty.id:
        return True
        
    abort(403)


def check_department_access(department_id):
    """
    Ensure HOD only accesses their own department.
    """
    if not current_user.is_authenticated:
        abort(403)
        
    if current_user.is_admin:
        return True
        
    if current_user.is_hod:
        hod_faculty = current_user.faculty_profile
        if hod_faculty and hod_faculty.department_id == department_id:
            return True
            
    abort(403)


def check_class_division_access(class_division):
    """
    Ensure faculty is assigned to this class or is HOD/Admin.
    """
    if not current_user.is_authenticated:
        abort(403)
        
    if current_user.is_admin:
        return True
        
    if current_user.is_hod:
        hod_faculty = current_user.faculty_profile
        if hod_faculty and hod_faculty.department_id == class_division.department_id:
            return True
            
    if current_user.is_faculty:
        faculty = current_user.faculty_profile
        if faculty and class_division in faculty.assigned_classes:
            return True
            
    abort(403)
