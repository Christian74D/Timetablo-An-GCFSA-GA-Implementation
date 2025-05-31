import pandas as pd
import numpy as np

def load_data(file_path):
    return pd.read_excel(file_path)

def split_theory_lab(df):
    split_rows = []

    for _, row in df.iterrows():
        theory = row.get('theory')
        lab = row.get('lab')

        theory = str(theory).strip()
        lab = str(lab).strip()

        theory_val = int(theory) if theory.isdigit() else np.nan
        lab_val = int(lab) if lab.isdigit() else np.nan

        if pd.notna(theory_val) and pd.notna(lab_val) and theory_val > 0 and lab_val > 0:
            theory_row = row.copy()
            theory_row['lab'] = 0
            split_rows.append(theory_row)

            lab_row = row.copy()
            lab_row['theory'] = 0
            split_rows.append(lab_row)
        else:
            split_rows.append(row)
        

    return pd.DataFrame(split_rows)

def save_to_excel(df, file_name):
    df.to_excel(file_name, index=False)

def theory_lab_split(src_path, dest_path):
    df = load_data(src_path)
    split_df = split_theory_lab(df)
    save_to_excel(split_df, dest_path)
    #print("Split theory and lab rows.")
