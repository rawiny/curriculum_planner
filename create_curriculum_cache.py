import pickle
import argparse
from data_models import Curriculum

def create_curriculum_cache(filepath="./static/data/curriculum.xlsx"):
    print("Processing Excel file to create cache...")
    curriculum = Curriculum(filepath=filepath)
    with open('curriculum_cache.pkl', 'wb') as f:
        pickle.dump(curriculum, f)
    print("Curriculum cache created successfully.")

parser = argparse.ArgumentParser(description='Create curriculum cache from Excel file.')
parser.add_argument('--filepath', type=str, default="./static/data/curriculum.xlsx", help='Path to the curriculum Excel file.')

args = parser.parse_args()
create_curriculum_cache(args.filepath)