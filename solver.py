from ortools.sat.python import cp_model

from data_models import Curriculum, StudentProfile

def find_optimal_plan(curriculum: Curriculum, student_profile: StudentProfile):
    """
    Finds the optimal plan for course completion based on completed courses and all available courses.

    Args:
        completed_courses (list): A list of completed course identifiers.
        all_courses (list): A list of all available course identifiers.

    Returns:
        list: A list of course identifiers representing the optimal plan for completion.
    """
    # Placeholder for the optimal plan logic
    
    # Create a optimization model
    model = cp_model.CpModel()
    
    study_vars = {}
    # Create decision variables
    for module in curriculum.module_names:
        study_vars[module] = model.NewBoolVar(f'study_{module}')
    
    # 1. Add constraints based on prerequisites
    for module in curriculum.prerequisites:
        if curriculum.prerequisites[module]:  # If there are prerequisites
            model.Add(sum(student_profile.passed[prereq] for prereq in curriculum.prerequisites[module]) >= len(curriculum.prerequisites[module]) * study_vars[module])
    
    # 2. Add constraints based on credit limits
    # Assuming a semester credit limit of 9 and minimum of 3
    model.Add(sum(study_vars[module] * curriculum.module_credits[module] for module in curriculum.module_names) <= curriculum.max_credits_per_term)
    model.Add(sum(study_vars[module] * curriculum.module_credits[module] for module in curriculum.module_names) >= curriculum.min_credits_per_term)

    # 3. Add constraints based on course availability in the term
    for module in curriculum.module_names:
        if curriculum.courses_in_term[module] == 0:
            model.Add(study_vars[module] == 0)    
    
    # 4. Add constraints based on the passed modules (the program will not suggest to study the passed modules)
    for module in curriculum.module_names:
        model.Add(study_vars[module] <= 1 - student_profile.passed[module])

    # 5. Add constraints based on timeslots (the program will not suggest to study the two or more modules that are in the same timeslot)
    for module in curriculum.timeslots:
        for other_module in curriculum.timeslots:
            if module != other_module and set(curriculum.timeslots[module]).intersection(set(curriculum.timeslots[other_module])):
                model.Add(study_vars[module] + study_vars[other_module] <= 1)
    
    # 6. Add constraints based on co-modules
    for module in curriculum.comodule:
        if curriculum.comodule[module]:  # If there are co-modules
            comod = curriculum.comodule[module][0]  # Assuming only one co-module for simplicity
            model.Add(study_vars[module] - study_vars[comod] + student_profile.passed[module] - student_profile.passed[comod] == 0)

    # 7. Add constraints based on already studied modules
    for module in curriculum.prior_exposure:
        if curriculum.prior_exposure[module]:  # If there are already studied modules
            studied_module = curriculum.prior_exposure[module][0]  # Assuming only one studied module for simplicity
            model.Add(study_vars[module] <= student_profile.studied[studied_module])
    
    # 8. (From 6th term onward,) Add constraints based on modules for minors (no more than 5 modules throughout the curriculum)
    if student_profile.n_terms_studied >= 6 and student_profile.chosen_minor and student_profile.chosen_minor != 'no minor' and student_profile.chosen_minor in curriculum.minors:
        model.Add(sum(study_vars[module] + student_profile.passed[module] for module in curriculum.minors[student_profile.chosen_minor]) <= 5)

    # 9. Add constraints based on paired modules for general education
    for pair in curriculum.gen_ed_pairs:
        model.Add(sum(study_vars[module] + student_profile.passed[module] for module in pair) <= 1)

    # 10. Add constraints based on other modules for general education (no more than 2 modules throughout the curriculum)
    model.Add(sum(study_vars[module] + student_profile.passed[module] for module in curriculum.general_education_groups) <= 2)

    # 11. (From 6th term onward,) Add constraints based on modules for minor, i.e., if a student has studied modules in a minor, they should continue to study modules in that minor.
    if student_profile.n_terms_studied >= 6 and student_profile.chosen_minor and student_profile.chosen_minor != 'no minor' and student_profile.chosen_minor in curriculum.minors:
        for other_minor in curriculum.minors:
            if other_minor != student_profile.chosen_minor:
                for module in curriculum.minors[other_minor]:
                    model.Add(study_vars[module] == 0)

    # 12. Add constraints about project modules. Students can register for project modules only if they have studied for 4 terms.
    if student_profile.n_terms_studied < 4:
        for module in curriculum.project_modules:
            model.Add(study_vars[module] == 0)

    # 13. Add constraints about free elective modules. Students can register for free elective modules only if they have studied for 5 terms.
    if student_profile.n_terms_studied <= 5:
        for module in curriculum.free_electives:
            model.Add(study_vars[module] == 0)
    
    # Objective: Maximize total credits (or minimize negative total credits)
    model.Minimize(curriculum.credit_requirement - sum(study_vars[module] * curriculum.module_credits[module] for module in curriculum.module_names))
    
    # Solve the model
    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        optimal_plan = [module for module in curriculum.module_names if solver.Value(study_vars[module]) == 1]
    elif status == cp_model.INFEASIBLE:
        print("The problem is infeasible.")
        optimal_plan = []
    else:
        print("No feasible solution found.")
        optimal_plan = []
    
    return optimal_plan