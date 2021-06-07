import numpy as np
import pandas as pd
from glob import glob
import os

path = 'G:/hela/res/'

def get_stats(folder):
    
    # Read files
    d_param = pd.read_csv(folder+"/parameters.txt", sep="\t",  index_col=0)
    d_sum = pd.read_csv(folder+"/summary.txt", sep="\t")
    d_ev = pd.read_csv(folder+"/evidence.txt", sep="\t", low_memory=False)
    d_pg = pd.read_csv(folder+"/proteinGroups.txt", sep="\t")
    d_msms = pd.read_csv(folder+"/msmsScans.txt", sep="\t")
    # Select only slice between 20 and 90 min for ms/ms intensity
    d_msms_2090 = d_msms[(d_msms["Retention time"] >= 20) &
       (d_msms["Retention time"] <= 90)]
    
    # Check for additionalInfo file.
    try:
        lines = []
        with open(folder+"/additionalInfo.txt") as f:
            lines = f.readlines()
        d_token = lines[0].split(",")
    except:
        print("No additionalInfo.txt file found. File size and date could not be read.")
        d_token = ["no path", 0.0, "2000-01-01"]
    
    print(d_token)
    
    # Check and load msScans file. This is missing in some MQ versions.
    try: 
        d_ms = pd.read_csv(folder+"/msScans.txt", sep="\t")
        d_ms_2090 = d_ms[(d_ms["Retention time"] >= 20) &
       (d_ms["Retention time"] <= 90)]
        ms_tic = int(np.median(d_ms_2090["Total ion current"]))
        ms_base = int(np.median(d_ms_2090["Base peak intensity"]))
    except:
        print("No MSscans.txt found in " + str(folder) + ". TIC values will be empty.")
        ms_tic = 0
        ms_base = 0

    # Calculate stats
    filename = d_sum["Raw file"][0] 
    timestamp = d_param.loc["Date of writing"].values[0]
    ms_count = int(d_sum[-1:]["MS"])
    msms_count = int(d_sum[-1:]["MS/MS"])
    ms_ratio = msms_count/ms_count
    pept_count_add = np.sum(d_sum["Peptide Sequences Identified"])-int(d_sum["Peptide Sequences Identified"][-1:])
    pept_count_unique = int(d_sum["Peptide Sequences Identified"][-1:])
    prot_count = len(d_pg.replace(0, np.nan).dropna(subset=['Intensity', 'Sequence coverage [%]']))
    uncal_mass_error = np.mean(d_ev["Uncalibrated mass error [ppm]"])
    ret_length = np.mean(d_ev["Retention length"].replace(1,np.nan).dropna())*60

    msms_tic = int(np.median(d_msms_2090["Total ion current"]))
    msms_base = int(np.median(d_msms_2090["Base peak intensity"]))

    filesize = float(d_token[1])
    filedate = str(d_token[2])

    # Determine FAIMS status  
    if len(d_sum) > 2 or "Fraction" in d_sum.columns:
        faims = "2CV"
    elif "1cv" in str(filename):
        faims = "1CV"
    else: 
        faims = "noFAIMS"

    # Determine producer
    if "MPI" in filename:
        producer = "MPI"
    elif "Pierce" in filename:
        producer = "Pierce"
    else:
        producer = "CPMS"

    # Determine gradient length
    if "1h" in filename:
        grad_len = "1h"
    else:
        grad_len = "2h"

    # Determine mass
    if "200ng" in filename:
        amount = 200
    else:
        amount = 500
                   
    return {"Filename": str(filename), 
            "analysis date": str(timestamp),
            "File size [MB]": round(filesize,2),
            "date created": filedate,
            "producer": producer,
            "gradient length": grad_len,
            "amount": amount,
            "FAIMS": faims,
            "MS": ms_count, 
            "MS/MS": msms_count, 
            "MS2/MS1 ratio": round(ms_ratio, 2), 
            "Peptide Seq Identified": pept_count_add, 
            "ProteinGroups": prot_count, 
            "Uncalibrated mass error [ppm]": round(uncal_mass_error,2), 
            "Retention length [s]": round(ret_length, 2), 
            "MS TIC": ms_tic, 
            "MS Base peak intensity": ms_base, 
            "MS/MS TIC": msms_tic, 
            "MS/MS Base peak intensity": msms_base
           }

def get_previous(path):
    # Loads data from pre-existing excel file with QC results.
    d_old = pd.read_excel(path+"hela_auto2.xlsx", index_col=0, engine='openpyxl')
    return d_old

# Check for pre-existing excel file and load if it exists.
try:
    # result_list = get_previous(path)
    # filenames = [get_previous(path)]["Filename"].values.tolist()
    result_table = pd.read_excel(path+"hela_auto2.xlsx", index_col=0, engine='openpyxl')
    filenames = result_table["Filename"].values.tolist()
except Exception as e: 
    print(e)
    result_table = []
    filenames = []
    print("No pre-existing table called hela_auto2.xlsx found.")

# Intialize counter for files that were skipped because they're already in the table.
old_count = 0

# Loop over all the MQ result folders, check for new ones and insert them into the table.
for i in glob(os.path.join(path, "*", "")):
    #check if its already there
    f = os.path.basename(os.path.normpath(str(i)))
    try:
        d_sum = pd.read_csv(i+"/summary.txt", sep="\t")
        filename = d_sum["Raw file"][0]
        if filename in filenames:
            #print(str(f) + " is already in the table.")
            old_count += 1
        else:
            row = pd.DataFrame([get_stats(i)])
            result_table = result_table.append(row)
            if row["FAIMS"].values[0] == "1CV":
                print(str(f) + " -> 1CV")
            elif row["FAIMS"].values[0] == "2CV":
                print(str(f) + " -> 2CV")
            elif row["FAIMS"].values[0] == "noFAIMS":
                print(str(f) + " -> noFAIMS")
            else:
                print(str(f) + " -> unknown FAIMS status")
    except Exception as e: 
        print(e)
        print("Folder " + str(f) + " is missing necessary files and could not be processed.")

# Save data back to excel file.
result_table.drop_duplicates().sort_values(by=['date created']).reset_index(drop=True).to_excel(path+"hela_auto2.xlsx")
print(str(old_count), "entries already in the tables.")
print("Done!")