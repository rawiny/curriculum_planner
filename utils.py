# --- utils.py ---
import pandas as pd

def process_column_to_dict(df: pd.DataFrame, key_column: str, value_column: str) -> dict:
    """Processes a DataFrame column of comma-separated strings into a dictionary."""
    processed_values = df[value_column].apply(lambda x: x.split(',') if pd.notna(x) else [])
    return dict(zip(df[key_column], processed_values))

def prepare_solver_input(curriculum, student_record) -> tuple[dict, dict]:
     x = {}
     z = {}
     for module in curriculum.module_names:
          if module in student_record:
               z[module] = 1 if student_record[module] != "W" and student_record[module] != "U" else 0 # get A - F grades
               x[module] = 1 if student_record[module] != "F" and student_record[module] != "W" and student_record[module] != "U" else 0 # get A - D grades
          else:
               x[module] = 0
               z[module] = 0
     return x, z