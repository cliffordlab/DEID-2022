"""
@author: Chase Fensore, previous work on phone functions from DEID 2008 repo
@date: 12 October 2022
BMI 500: De-identification lab
"""

from distutils.command import check
import re
import sys
import spacy
from spacy import displacy
NER = spacy.load("en_core_web_lg")

phone_pattern ='(\d{3}[-\.\s/]??\d{3}[-\.\s/]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s/]??\d{4})'

# compiling the reg_ex would save sime time!
ph_reg = re.compile(phone_pattern)

def check_for_name(patient, note, chunk, output_handle):
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
        Search the entire chunk for name occurances. Find the location of these occurances 
        relative to the start of the chunk, and output these to the output_handle file. 
        If there are no occurances, only output Patient X Note Y (X and Y are passed in as inputs) in one line.
        - Use the spaCy large NER in english with NER as "PERSON".

    """
    # The perl code handles texts a bit differently, 
    # we found that adding this offset to start and end positions would produce the same results
    offset = 27

    # For each new note, the first line should be Patient X Note Y and then all the personal information positions
    output_handle.write('Patient {}\tNote {}\n'.format(patient,note))

    # search the whole chunk, and find every position that matches the spaCy criteria for 'PERSON'
    # for each one write the results: "Start Start END"
    # Also for debugging purposes display on the screen (and don't write to file) 
    # the start, end and the actual personal information that we found
    doc = NER(chunk)
    
    ents = [(e.text, e.start_char, e.end_char, e.label_) for e in doc.ents]
    name_ents = [e for e in ents if e[3] == 'PERSON'] # e[3] is e.label_
    print("ENTS: ", ents)
    print("NAME ENTS", name_ents)
    
    l_chunk = ""
    r_chunk = chunk
    for e in name_ents:
            # debug print, 'end=" "' stops print() from adding a new line
            print(patient, note,end=' ')
 
            #start_pos = chunk.index(str(name)) # Index of name in chunk.
            #end_pos = start_pos + len(str(name)) # Index of end of name.

            start_pos = len(r_chunk) - r_chunk.index(e[0]) + len(l_chunk) # pos of start of word in chunk
            end_pos =  start_pos + len(e[0]) # pos of end of chunk

            print((start_pos-offset),end_pos-offset) # name.group()
                    
            result = str(start_pos-offset) + ' ' + str(start_pos-offset) + ' '+ str(end_pos-offset) 
            
            # write the result to one line of output
            output_handle.write(result+'\n')
    


def check_for_date(patient,note,chunk, output_handle):
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
        Search the entire chunk for date occurances. Find the location of these occurances 
        relative to the start of the chunk, and output these to the output_handle file. 
        If there are no occurances, only output Patient X Note Y (X and Y are passed in as inputs) in one line.
        - Use the spaCy large NER in english with NER as "DATE".

    """
    # The perl code handles texts a bit differently, 
    # we found that adding this offset to start and end positions would produce the same results
    offset = 27

    # For each new note, the first line should be Patient X Note Y and then all the personal information positions
    output_handle.write('Patient {}\tNote {}\n'.format(patient,note))

    # search the whole chunk, and find every position that matches the spaCy criteria for 'PERSON'
    # for each one write the results: "Start Start END"
    # Also for debugging purposes display on the screen (and don't write to file) 
    # the start, end and the actual personal information that we found
    doc = NER(chunk)
    
    ents = [(e.text, e.start_char, e.end_char, e.label_) for e in doc.ents]
    name_ents = [e for e in ents if e[3] == 'DATE'] # e[3] is e.label_
    
    # Divide into left and right chunks of init chunk. Avoids indexing duplicates.
    l_chunk = ""
    r_chunk = chunk
    for e in name_ents:
            # debug print, 'end=" "' stops print() from adding a new line
            print(patient, note,end=' ')
 
            #start_pos = chunk.index(str(name)) # Index of name in chunk.
            #end_pos = start_pos + len(str(name)) # Index of end of name.

            start_pos = len(r_chunk) - r_chunk.index(e[0]) + len(l_chunk) # pos of start of word in chunk
            end_pos =  start_pos + len(e[0]) # pos of end of chunk

            print((start_pos-offset),end_pos-offset) # name.group() 
                    
            result = str(start_pos-offset) + ' ' + str(start_pos-offset) + ' '+ str(end_pos-offset) 
            
            # write the result to one line of output
            output_handle.write(result+'\n')



def check_for_phone(patient,note,chunk, output_handle):
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
        Search the entire chunk for phone number occurances. Find the location of these occurances 
        relative to the start of the chunk, and output these to the output_handle file. 
        If there are no occurances, only output Patient X Note Y (X and Y are passed in as inputs) in one line.
        Use the precompiled regular expression to find phones.
    """
    # The perl code handles texts a bit differently, 
    # we found that adding this offset to start and end positions would produce the same results
    offset = 27

    # For each new note, the first line should be Patient X Note Y and then all the personal information positions
    output_handle.write('Patient {}\tNote {}\n'.format(patient,note))

    # search the whole chunk, and find every position that matches the regular expression
    # for each one write the results: "Start Start END"
    # Also for debugging purposes display on the screen (and don't write to file) 
    # the start, end and the actual personal information that we found
    for match in ph_reg.finditer(chunk):
                
            # debug print, 'end=" "' stops print() from adding a new line
            print(patient, note,end=' ')
            print((match.start()-offset),match.end()-offset, match.group())
                
            # create the string that we want to write to file ('start start end')    
            result = str(match.start()-offset) + ' ' + str(match.start()-offset) +' '+ str(match.end()-offset) 
            
            # write the result to one line of output
            output_handle.write(result+'\n')

            
            
def deid_phone(text_path= 'id.text', output_path = 'phone.phi'):
    """
    Inputs: 
        - text_path: path to the file containing patient records
        - output_path: path to the output file.
    
    Outputs:
        for each patient note, the output file will start by a line declaring the note in the format of:
            Patient X Note Y
        then for each phone number found, it will have another line in the format of:
            start start end
        where the start is the start position of the detected phone number string, and end is the detected
        end position of the string both relative to the start of the patient note.
        If there is no phone number detected in the patient note, only the first line (Patient X Note Y) is printed
        to the output
    Screen Display:
        For each phone number detected, the following information will be displayed on the screen for debugging purposes 
        (these will not be written to the output file):
            start end phone_number
        where `start` is the start position of the detected phone number string, and `end` is the detected end position of the string
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
                    # Now we have a full patient note stored in `chunk`, along with patient numerb and note number
                    # pass all to check_for_phone to find any phone numbers in note.
                    
                    #check_for_phone(patient,note,chunk.strip(), output_file)
                    check_for_name(patient,note,chunk.strip(), output_file)
                    
                    # initialize the chunk for the next note to be read
                    chunk = ''
                
if __name__== "__main__":
        
    
    
    deid_phone(sys.argv[1], sys.argv[2])
    