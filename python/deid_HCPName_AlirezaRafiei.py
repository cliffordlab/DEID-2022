'''
# Modified by: Alireza Rafiei
# Date: 16-Oct-2022
# HW8 BMI500 - de-identification

This de-identification code aims to automatic removal of protected health information (PHI) in free text
from medical data. For more information about the data, gold-standard corpus, and the developed packages, see
this reference: https://www.physionet.org/physiotools/deid/

The current script focuses on the PHI de-identification of HCPName from attributes of the medical free texts.
The two following functions (check_for_HCPName, deid_HCPName) extract and reveal the location of the existing
HCPNames from the available texts.

How to run the code?
    python deid_HCPName_AlirezaRafiei.py <input_filename> <output_filename>
    # input_filename (.txt): Free medical text (e.g., id.txt)
    # output_filename (.phi): Output file with patient name records and the extracted HCPName (e.g., HCPName.phi)
    
How to evaluate the results?
    The performance of the script can be evaluated using the stats.py code (presented in this repo)
    and the following command
    python stats.py id.deid id-phi.phrase HPCName_AlirezaRafiei.phi
    
Required libraries: 're', 'sys'

'''


import re
import sys


# ========================
# ==  Identify HCPName  ==
# ========================

HCPName_pattern = "((?i)(W\/|\s)dr\.?\s)|([(.]dr\.?\s)|((?i)(W\/|\s)dtr\.?\s)|((?i)(W\/|\s)drs\.?\s)"
# Detection of "dr" and "dtr" words are the keys to identifying HCPNames. These works can be in a sentence or in a bracket.
# Also, "dr" can be used as the plural word "drs" in medical texts.

# compiling the reg_ex would save sime time!
HCPName_reg = re.compile(HCPName_pattern)


def check_for_HCPName(patient, note, chunk, output_handle):
    """
    Inputs:
        - patient: Patient Number, will be printed in each occurance of personal information found
        - note: Note Number, will be printed in each occurance of personal information found
        - chunk: one whole record of a patient
        - output_handle: an opened file handle. The results will be written to this file.
            to avoid the time intensive operation of opening and closing the file multiple times
            during the de-identification process, the file is opened beforehand and the handle is passed
            to this function. 
    Logic:
        Search the entire chunk for HCPName occurances. Find the location of these occurances 
        relative to the start of the chunk, and output these to the output_handle file. 
        If there are no occurances, only output Patient X Note Y (X and Y are passed in as inputs) in one line.
        Use the precompiled regular expression to find HCPNames.
    """
    # The perl code handles texts a bit differently, 
    # we found that adding this offset to start and end positions would produce the same results
    offset = 27

    # For each new note, the first line should be Patient X Note Y and then all the personal information positions
    output_handle.write('Patient {}\tNote {}\n'.format(patient, note))

    # search the whole chunk, and find every position that matches the regular expression
    # for each one write the results: "Start Start END"
    # Also for debugging purposes display on the screen (and don't write to file) 
    # the start, end and the actual personal information that we found
    for match in HCPName_reg.finditer(chunk):
            

            # debug print, 'end=" "' stops print() from adding a new line
            print(patient, note,end=' ')
            print((match.start()-offset), match.end()-offset, match.group())
                
            # create the string that we want to write to file ('start start end')    
            result = str(match.start()-offset) + ' ' + str(match.start()-offset) +' '+ str(match.end()-offset) 
            
            # write the result to one line of output
            output_handle.write(result+'\n')

            
            
def deid_HCPName(text_path= 'id.text', output_path = 'HPCName_AlirezaRafiei.phi'):
    """
    Inputs: 
        - text_path: path to the file containing patient records
        - output_path: path to the output file.
    
    Outputs:
        for each patient note, the output file will start by a line declaring the note in the format of:
            Patient X Note Y
        then for each HCPName found, it will have another line in the format of:
            start start end
        where the start is the start position of the detected HCPName string, and end is the detected
        end position of the string both relative to the start of the patient note.
        If there is no DtaeYear detected in the patient note, only the first line (Patient X Note Y) is printed
        to the output
    Screen Display:
        For each HCPName detected, the following information will be displayed on the screen for debugging purposes 
        (these will not be written to the output file):
            start end HCPName
        where `start` is the start position of the detected HCPName string, and `end` is the detected end position of the string
        both relative to the start of patient note.
    
    """
    # start of each note has the patter: START_OF_RECORD=PATIENT||||NOTE||||
    # where PATIENT is the patient number and NOTE is the note number.
    start_of_record_pattern = '^start_of_record=(\d+)\|\|\|\|(\d+)\|\|\|\|$'

    # end of each note has the patter: ||||END_OF_RECORD
    end_of_record_pattern = '\|\|\|\|END_OF_RECORD$'

    # open the output file just once to save time on the time intensive IO
    with open(output_path,'w+') as output_file:
        with open(text_path) as text:
            # initilize an empty chunk. Go through the input file line by line
            # whenever we see the start_of_record pattern, note patient and note numbers and start 
            # adding everything to the 'chunk' until we see the end_of_record.
            chunk = ''
            for line in text:
                record_start = re.findall(start_of_record_pattern,line,flags=re.IGNORECASE)
                if len(record_start):
                    patient, note = record_start[0]
                chunk += line

                # check to see if we have seen the end of one note
                record_end = re.findall(end_of_record_pattern, line,flags=re.IGNORECASE)

                if len(record_end):
                    # Now we have a full patient note stored in `chunk`, along with patient number and note year
                    # pass all to check_for_year to find any years in note.
                    check_for_HCPName(patient,note,chunk.strip(), output_file)
                    
                    # initialize the chunk for the next note to be read
                    chunk = ''
                
if __name__== "__main__":
        
    deid_HCPName(sys.argv[1], sys.argv[2])
        
