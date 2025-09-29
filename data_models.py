import pandas as pd
from utils import process_column_to_dict

class Curriculum:
    """Holds all the data about the school's curriculum."""
    def __init__(self, filepath="./data/curriculum.xlsx"):
        # In a real app, this data will be loaded from an Excel file here.
        self.data = pd.read_excel(filepath, sheet_name=None)

        """Sheet: Requirements"""
        # Total credits required to graduate
        requirements_sheet = self.data['Requirements']
        self.credit_requirement = requirements_sheet['value'][0]
        self.min_credits_per_term = requirements_sheet['value'][1]
        self.max_credits_per_term = requirements_sheet['value'][2]
        
        """Sheet: Courses"""
        # Module names
        courses_sheet = self.data['Courses']
        self.module_names = courses_sheet['course_id']
        # Module credits
        self.module_credits = dict(zip(courses_sheet['course_id'], courses_sheet['credits']))

        # Prerequisites
        self.prerequisites = process_column_to_dict(courses_sheet, 'course_id', 'prerequisites')
                
        # The module that requires students to study before (prior exposure)
        self.prior_exposure = process_column_to_dict(courses_sheet, 'course_id', 'prior_exposure')

        # The module that is usually studied with another module (co-requisite)
        self.comodule = process_column_to_dict(courses_sheet, 'course_id', 'co_modules')

        # Assumed time slots for scheduling/clash detection
        self.timeslots = process_column_to_dict(courses_sheet, 'course_id', 'time_slots')
        
        # That module opens in that term (1 = available, 0 = not available)
        self.courses_in_term = dict(zip(courses_sheet['course_id'], courses_sheet['is_available_term']))
        
        """Sheet: Minors"""
        minors_sheet = self.data['Minors']
        # modules for different minors
        self.minors = process_column_to_dict(minors_sheet, 'minor_name', 'required_courses')
        
        """Sheet: GenEd"""
        # The other gen ed modules
        self.general_education_groups = self.data['GenEd']['course_id'].tolist()

        """Sheet: pairedGenEd"""
        # The gen ed module pairs that must be taken one of a pair
        processed_values = self.data['pairedGenEd']['Groups'].apply(lambda x: x.split(',') if pd.notna(x) else [])
        self.gen_ed_pairs = [tuple(group) for group in processed_values]       

        """Sheet: Project"""        
        # Project modules
        self.project_modules = self.data['Projects']['course_id'].tolist()
        
        """Sheet: Free Electives"""
        # Free elective modules
        self.free_electives = self.data['Free electives']['course_id'].tolist()


class StudentProfile:
    """Holds all the data for a specific student."""
    def __init__(self, passed_modules, studied_modules, terms_studied, minor='no minor'):
        self.passed = passed_modules
        self.studied = studied_modules
        self.n_terms_studied = terms_studied
        # You could also add the student's chosen minor here
        self.chosen_minor = minor



