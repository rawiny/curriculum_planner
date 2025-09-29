import pickle
from flask import Flask, render_template, request
#from flask_sqlalchemy import SQLAlchemy
from data_models import Curriculum, StudentProfile
import solver
from utils import prepare_solver_input

app = Flask(__name__)
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///curriculum_planner.db'
#db = SQLAlchemy(app)

# load curriculum data from cache
try:
    print("Loading curriculum from cache (pickle file)...")
    # The 'rb' means we are reading in binary mode.
    with open('curriculum_cache.pkl', 'rb') as f:
        curriculum_data = pickle.load(f)
    print("Curriculum loaded successfully from cache.")
except FileNotFoundError:
    print("FATAL ERROR: 'curriculum_cache.pkl' not found.")
    print("--> Please run 'create_curriculum_cache.py' first to generate the cache file.")
    curriculum_data = None

courses = {}
minors = curriculum_data.minors.keys() if curriculum_data else {}

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Process form data here
        term = request.form.get('term')
        if term is not None:
            n_terms_studied = int(term)
        else:
            n_terms_studied = 1  # Default to 1 if not provided
        minor_val = request.form.get('minors')
        minor = minor_val.lower() if minor_val is not None else "general"
        # Prepare the student record from the courses dictionary
        x, z = prepare_solver_input(curriculum_data, courses)

        student_profile = StudentProfile(passed_modules=x, studied_modules=z, terms_studied=n_terms_studied, minor=minor)

        if curriculum_data is not None:
            optimal_modules = solver.find_optimal_plan(curriculum_data, student_profile)
            return render_template('index.html', minors=minors, courses=courses, optimal_modules=optimal_modules)
    return render_template('index.html', minors=minors, courses=courses)

@app.route('/add_course', methods=['POST'])
def add_course():
    course_name = request.form.get('course')
    course_grade = request.form.get('grade')
    if course_name and course_grade:
        courses[course_name] = course_grade
    return render_template('index.html', minors=minors, courses=courses)

@app.route('/remove_course/<course>', methods=['POST', 'GET'])
def remove_course(course):
    if course in courses:
        del courses[course]
    return render_template('index.html', minors=minors, courses=courses)

if __name__ == '__main__':
    app.run(debug=True)