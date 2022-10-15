# Modified by: Cristian Barrera
# Date: 10/13/2022
# Description: PHI deidentification, specifically for HCPName

import re
import sys

# More phone patterns included for Phone category
# pattern given by the file deid.py
phone_pattern_1 = '(\d{3}[-\.\s/]??\d{3}[-\.\s/]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s/]??\d{4})'
# patterns for pagers
phone_pattern_2 = 'Pager: \#\d{5}'
phone_pattern_3 = 'Pager \#\d{5}'
phone_pattern_4 = 'Pager \d{5}'
phone_pattern_5 = 'PG \d{5}'
phone_pattern_6 = 'PG \#\d{5}'
phone_pattern_7 = 'pg \#\d{5}'
phone_pattern_8 = 'pg \d{5}'
# patterns for phone numbers with moved '-'
phone_pattern_9 = '\d{3}- \d{3}- \d{4}'
phone_pattern_10 = '\d{3} -\d{3} -\d{4}'

# compiling the reg_ex would save some time!
ph_reg = re.compile(phone_pattern_1 
                     + "|" + phone_pattern_2
                     + "|" + phone_pattern_3
                     + "|" + phone_pattern_4
                     + "|" + phone_pattern_5
                     + "|" + phone_pattern_6
                     + "|" + phone_pattern_7
                     + "|" + phone_pattern_8
                     + "|" + phone_pattern_9
                     + "|" + phone_pattern_10)

# Pattern for Patient names
ptname_pattern_1 = "^([a-zA-Z]{2,}\\s[a-zA-Z]{1,}'?-?[a-zA-Z]{2,}\\s?([a-zA-Z]{1,})?)"
ptname_reg = re.compile(ptname_pattern_1)

# pattern for Patient doctor or doctor in charge or referal
# Two name dr. pattern -> dr. name lastname
#hcpname_pattern_1 = '(W\/|\s)dr\.?\s[a-zA-Z]+\s[a-zA-Z]+'
hcpname_pattern_1 = 'dr\.?\s[a-zA-Z]+\.?\s[a-zA-Z]+'
# Single name dr. pattern -> dr. name
hcpname_pattern_2 = 'Dr\.?\s[a-zA-Z]+\.?\s[a-zA-Z]+'
# capital Dr with two name -> Dr. name lastname
hcpname_pattern_3 = 'DR\.?\s[a-zA-Z]+\.?\s[a-zA-Z]+'
# Two name dr. pattern with - first name
hcpname_pattern_4 = 'dr\.?\s[a-zA-Z]+-[a-zA-Z]+\.?\s[a-zA-Z]+'
# Two name dr. pattern with - first name and second name
hcpname_pattern_5 = 'dr\.?\s[a-zA-Z]+-[a-zA-Z]+\.?\s[a-zA-Z]+'
hcpname_pattern_33 = 'DR\.?\s[a-zA-Z]+-[a-zA-Z]+\.?'
hcpname_pattern_34 = 'Dr\.?\s[a-zA-Z]+-[a-zA-Z]+\.?'
# Pattern with a single letter name and maybe last name
hcpname_pattern_6 = 'dr\.?\s\w{1}\.?\s[a-zA-Z]+'
hcpname_pattern_7 = 'Dr\.?\s\w{1}\.?\s[a-zA-Z]+'
hcpname_pattern_8 = 'DR\.?\s\w{1}\.?\s[a-zA-Z]+'
# single
hcpname_pattern_9 = 'dr\.?\s[a-zA-Z]+\)'
hcpname_pattern_10 = 'Dr\.?\s[a-zA-Z]+\)'
hcpname_pattern_11 = 'DR\.?\s[a-zA-Z]+\)'

hcpname_pattern_12 = 'dr\.?\s[a-zA-Z]+\.'
hcpname_pattern_13 = 'Dr\.?\s[a-zA-Z]+\.'
hcpname_pattern_14 = 'DR\.?\s[a-zA-Z]+\.'

hcpname_pattern_15 = 'dr\.?\s[a-zA-Z]+\,'
hcpname_pattern_16 = 'Dr\.?\s[a-zA-Z]+\,'
hcpname_pattern_17 = 'DR\.?\s[a-zA-Z]+\,'

# MD related
hcpname_pattern_19 = 'md\.?\s[a-zA-Z]+'
hcpname_pattern_20 = 'MD\.?\s[a-zA-Z]+'
hcpname_pattern_21 = 'Md\.?\s[a-zA-Z]+'
hcpname_pattern_22 = 'md\.?\s[a-zA-Z]+\.?\s[a-zA-Z]+'
hcpname_pattern_23 = 'MD\.?\s[a-zA-Z]+\.?\s[a-zA-Z]+'
hcpname_pattern_24 = 'Md\.?\s[a-zA-Z]+\.?\s[a-zA-Z]+'

# Use the same from the beggining but single name for a dr
hcpname_pattern_25 = 'dr\.?\s[a-zA-Z]+'
hcpname_pattern_26 = 'dr\.?\s[a-zA-Z]+'
# Single name dr. pattern -> dr. name
hcpname_pattern_27 = 'Dr\.?\s[a-zA-Z]+'
# capital Dr with two name -> Dr. name lastname
hcpname_pattern_28 = 'DR\.?\s[a-zA-Z]+'
# Two name dr. pattern with - first name
hcpname_pattern_29 = 'dr\.?\s[a-zA-Z]+-[a-zA-Z]+'
# Two name dr. pattern with - first name and second name
hcpname_pattern_30 = 'dr\.?\s[a-zA-Z]+-[a-zA-Z]+'

# S. related
hcpname_pattern_31 = 'HOUSE STAFF\s[a-zA-Z]+\s[a-zA-Z]+'
hcpname_pattern_32 = 'CASEWORKER\s[a-zA-Z]+\s[a-zA-Z]+'

# Prular Doctors (DRS)
hcpname_pattern_33 = 'Drs\'\s[a-zA-Z]+\s[a-zA-Z]+\s[a-zA-Z]+'
hcpname_pattern_34 = 'DRS\s[a-zA-Z]+\s[a-zA-Z]+\s[a-zA-Z]+'

# Other style (dtr)
hcpname_pattern_18 = 'docter\s[a-zA-Z]+'
hcpname_pattern_35 = 'dtr\s[a-zA-Z]+\s[a-zA-Z]+'

# Nurse related
hcpname_pattern_36 = 'nurse\s[a-zA-Z]+\s[a-zA-Z]+'
hcpname_pattern_37 = 'NURSE\s[a-zA-Z]+\s[a-zA-Z]+'
hcpname_pattern_38 = 'NURSES\s[a-zA-Z]+\s[a-zA-Z]+'
hcpname_pattern_39 = 'Nurse\s[a-zA-Z]+\s[a-zA-Z]+'

# RRT related
hcpname_pattern_40 = '[a-zA-Z]+\s[a-zA-Z]+\.?\s[a-zA-Z]+\,\sRRT'
# if name contains a '-' as last name
hcpname_pattern_41 = '[a-zA-Z]+\s[a-zA-Z]+\.?\s[a-zA-Z]+-[a-zA-Z]+[a-zA-Z]+\,\sRRT'
# If a first name is a letter only; it may overlap others
hcpname_pattern_42 = '\w{1}\.?\s[a-zA-Z]+\,\sRRT'
# For reverse MD also
hcpname_pattern_43 = '[a-zA-Z]+\.?\s[a-zA-Z]+\,\sMD'
hcpname_pattern_44 = '[a-zA-Z]+\.?\s[a-zA-Z]+\,MD'

# For , RN
hcpname_pattern_45 = '[a-zA-Z]+\.?\s[a-zA-Z]+\, RN'

# Some may not be useful as can be covered by some patterns At least for this case
hcpname_reg = re.compile(hcpname_pattern_1 
                     + "|" + hcpname_pattern_2 + "|" + hcpname_pattern_3
                     + "|" + hcpname_pattern_4 + "|" + hcpname_pattern_5
                     + "|" + hcpname_pattern_6 + "|" + hcpname_pattern_7
                     + "|" + hcpname_pattern_8 + "|" + hcpname_pattern_9
                     + "|" + hcpname_pattern_10 + "|" + hcpname_pattern_11
                     + "|" + hcpname_pattern_12 + "|" + hcpname_pattern_13
                     + "|" + hcpname_pattern_14 + "|" + hcpname_pattern_15
                     + "|" + hcpname_pattern_16 + "|" + hcpname_pattern_17
                     + "|" + hcpname_pattern_18 + "|" + hcpname_pattern_19
                     + "|" + hcpname_pattern_20 + "|" + hcpname_pattern_21
                     + "|" + hcpname_pattern_22 + "|" + hcpname_pattern_23
                     + "|" + hcpname_pattern_24 + "|" + hcpname_pattern_25
                     + "|" + hcpname_pattern_26 + "|" + hcpname_pattern_27
                     + "|" + hcpname_pattern_28 + "|" + hcpname_pattern_29
                     + "|" + hcpname_pattern_30 + "|" + hcpname_pattern_31
                     + "|" + hcpname_pattern_32 + "|" + hcpname_pattern_33
                     + "|" + hcpname_pattern_34 + "|" + hcpname_pattern_35
                     + "|" + hcpname_pattern_36 + "|" + hcpname_pattern_37
                     + "|" + hcpname_pattern_38 + "|" + hcpname_pattern_39
                     + "|" + hcpname_pattern_40 + "|" + hcpname_pattern_41
                     + "|" + hcpname_pattern_42 + "|" + hcpname_pattern_43
                     + "|" + hcpname_pattern_44 + "|" + hcpname_pattern_45)

# Read doctor first and last name files
dr_first_ls = open("../lists/doctor_first_names-cristian-barrera.txt", "r")
dr_first_ls = dr_first_ls.read()
dr_second_ls = open("../lists/doctor_last_names-cristian-barrera.txt", "r")
dr_second_ls = dr_second_ls.read()

# Class: Phone
def check_for_phone_v2(patient,note,chunk, output_handle):
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

def check_for_doctor_name(patient,note,chunk, output_handle):
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
    for match in hcpname_reg.finditer(chunk):
            # debug print, 'end=" "' stops print() from adding a new line
            #print(patient, note,end=' ')
            #print((match.start()-offset),match.end()-offset, match.group())
            # Save the complete set of pattern
            hcp_pat = match.group()
            # Get the initial value position and last
            hcp_pat_s = match.start()-offset
            # Get the original length of the word
            # Split the pattern, remove the 'dr' as we know first is always dr
            #print(hcp_pat)
            spl_pat = hcp_pat.split()
            # Check if it has RRT
            if 'RRT' in spl_pat:
                # If it has a RRT, reverse the list, so RRT is at the beggining
                spl_pat = spl_pat[::-1]
            # Check if it has MD
            if 'MD' in spl_pat:
                # If it has a MD, reverse the list
                spl_pat = spl_pat[::-1]
            # Get the beggining and end of the position of individual names
            patw_beg = []
            patw_end = []
            patw_tmp = []
            # Check each of the splitted strings for possible names
            for a in spl_pat:
                # Add the length of the word
                patw_tmp.append(len(a)+1)
                # Sum the length of the word and words, with the x_position of the 
                # initial match, substract the value of the word to get the exact position
                # Also remove any other symbol that is not a letter and substract 2 positions
                patw_beg.append(sum(patw_tmp) + hcp_pat_s - len(a)-len(re.sub('[a-zA-Z]','',a)) - 2)
                # Similarly, for the end of the string, we substract 3. It seems to be related 
                # to space between strings/words
                patw_end.append(sum(patw_tmp) + hcp_pat_s - len(re.sub('[a-zA-Z]','',a)) - 3)
            # remove the initial words, which is related to DR, MR, RRT, etc
            # Also remove their initial positions as it will not be used
            patw_beg.pop(0)
            patw_end.pop(0)
            spl_pat.pop(0)
            # create the string that we want to write to file ('start start end')
            # Check for start, end, word and position of the word
            for a,b,c,d in zip(patw_beg,patw_end,spl_pat,range(0,len(spl_pat))):
                # if a word contains a symbol, remove it
                c = re.sub('[^a-zA-Z]','',c)
                # if the position is second (after first name) check if it is 
                # a name and not a typical connector. If not, skip
                if d == 1: 
                    if c.upper() == 'AND' or c.upper() == 'IN' or c.upper() == 'IS' or c.upper() == 'ON' or c.upper() == 'TO':
                        continue
                # Check if the word is allocated in the name and surname lists
                # as it uses /n /n between the words, we included them
                if '\n' + c.upper()+'\n' in dr_first_ls or '\n' + c.upper() + '\n' in dr_second_ls:
                    # get the result in a single variable
                    result = str(a) + ' ' + str(a) +' '+ str(b)
                    # write the result to one line of output
                    output_handle.write(result+'\n')
                    # print out the found patient id, position and words
                    print(patient, note,end=' ')
                    print(a,b,c)
                else:
                    continue
            


def deid_run(text_path= 'id.text', output_path = 'deid-cristian-barrera.phi'):
    """
    Inputs: 
        - text_path: path to the file containing patient records
        - output_path: path to the output file.
    
    Outputs:
        for each patient note, the output file will start by a line declaring the note in the format of:
            Patient X Note Y
        then for each pattern (e.g. phone number) found, it will have another line in the format of:
            start start end
        where the start is the start position of the detected pattern string, and end is the detected
        end position of the string both relative to the start of the patient note.
        If there is no a pattern detected in the patient note, only the first line (Patient X Note Y) is printed
        to the output
    Screen Display:
        For each pattern detected, the following information will be displayed on the screen for debugging purposes 
        (these will not be written to the output file):
            start end pattern_found
        where `start` is the start position of the detected pattern string, and `end` is the detected end position of the string
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
                    # Now we have a full patient note stored in `chunk`, along with patient number and note number
                    # pass all to the differnt pattern recogn. to find any pattern in note.
                    #%% Check for Phone Numbers (also Pager numbers)
                    # check_for_phone_v2(patient,note,chunk.strip(), output_file)
                    # Check for Doctor names
                    check_for_doctor_name(patient,note,chunk.strip(), output_file)
                    # initialize the chunk for the next note to be read
                    chunk = ''
 
if __name__== "__main__":
    deid_run(sys.argv[1], sys.argv[2])
