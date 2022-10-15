import re
import sys
# The below import is needed to allow multiple iterators to be consumed at once (checking for different date formats)
from itertools import chain

# This catches dates like dd/mm/yyyy or dd/mm/yy. Validates day and month to ensure it is within a valid date range. Excludes just zeros.
# The separators can be either "/", "-", ".".
date_pattern_one = '(0?[1-9]|[12][0-9]|3[01])[\/\-\.](0?[1-9]|1[012])[\/\-\.](\d{4}|\d{2})'

# This catches dates like mm/dd/yyyy or mm/dd/yy. Validates month and day to ensure it is within a valid date range. Excludes just zeros.
# The separators can be either "/", "-", or ".".
date_pattern_two = '(0?[1-9]|1[012])[\/\-\.](0?[1-9]|[12][0-9]|3[01])[\/\-\.](\d{4}|\d{2})'

# This catches dates like yyyy/mm/dd or yy/mm/dd. Validates month and day to ensure it is within a valid date range. Excludes just zeros.
# The separators can be either "/", "-", or ".".
date_pattern_three = '(\d{4}|\d{2})[\/\-\.](0?[1-9]|1[012])[\/\-\.](0?[1-9]|[12][0-9]|3[01])'

# This catches dates like yyyy/dd/mm or yy/dd/mm. Validates month and day to ensure it is within a valid date range. Excludes just zeros.
# The separators can be either "/", "-", or ".".
date_pattern_four = '(\d{4}|\d{2})[\/\-\.](0?[1-9]|[12][0-9]|3[01])[\/\-\.](0?[1-9]|1[012])'

# This catches dates like dd/mm. Validates month and day to ensure it is within a valid date range. Excludes just zeros.
date_pattern_five = '(0?[1-9]|[12][0-9]|3[01])[\/](0?[1-9]|1[012])'

# This catches dates like mm/dd. Validates month and day to ensure it is within a valid date range. Excludes just zeros.
date_pattern_six = '(0?[1-9]|1[012])[\/](0?[1-9]|[12][0-9]|3[01])'

# This pattern ensures that the date has the same kind of separator. It rejects dates like "08/09-2022", etc.
# This will only be run after validating one of the above two regular expressions.
same_separator_pattern = '(\d+\.\d+\.\d+)|(\d+ \d+ \d+)|(\d+\-\d+\-\d+)|(\d+\/\d+\/\d+)'

# This pattern serves to ensure that just month/day or day/month combinations are allowed through, as the above separator pattern is exclusive to year formats
no_year_sep_pattern = '(^\d+\/\d+$)'

# compiling the reg_ex would save sime time!
compiled_dp_one = re.compile(date_pattern_one)
compiled_dp_two = re.compile(date_pattern_two)
compiled_dp_three = re.compile(date_pattern_three)
compiled_dp_four = re.compile(date_pattern_four)
compiled_dp_five = re.compile(date_pattern_five)
compiled_dp_six = re.compile(date_pattern_six)
compiled_separator_pattern = re.compile(same_separator_pattern)
compiled_noyearsep = re.compile(no_year_sep_pattern)


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
        Use the precompiled regular expressions to find dates.
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
    for first_match in chain(compiled_dp_one.finditer(chunk), compiled_dp_two.finditer(chunk), compiled_dp_three.finditer(chunk), compiled_dp_four.finditer(chunk), compiled_dp_five.finditer(chunk), compiled_dp_six.finditer(chunk)):
    	if compiled_separator_pattern.search(first_match.group()) or compiled_noyearsep.search(first_match.group()):
        	# debug print, 'end=" "' stops print() from adding a new line
        	print(patient, note,end=' ')
        	print((first_match.start()-offset),first_match.end()-offset, first_match.group())
                
        	# create the string that we want to write to file ('start start end')    
        	result = str(first_match.start()-offset) + ' ' + str(first_match.start()-offset) +' '+ str(first_match.end()-offset) 
            
        	# write the result to one line of output
        	output_handle.write(result+'\n')

            
            
def deid_date(text_path= 'id.text', output_path = 'phone.phi'):
    """
    Inputs: 
        - text_path: path to the file containing patient records
        - output_path: path to the output file.
    
    Outputs:
        for each patient note, the output file will start by a line declaring the note in the format of:
            Patient X Note Y
        then for each date found, it will have another line in the format of:
            start start end
        where the start is the start position of the detected date, and end is the detected
        end position of the string both relative to the start of the patient note.
        If there is no date detected in the patient note, only the first line (Patient X Note Y) is printed
        to the output
    Screen Display:
        For each date detected, the following information will be displayed on the screen for debugging purposes 
        (these will not be written to the output file):
            start end phone_number
        where `start` is the start position of the detected date, and `end` is the detected end position of the string
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
        	# initialize an empty chunk. Go through the input file line by line
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
                    check_for_date(patient,note,chunk.strip(), output_file)
                    
                    # initialize the chunk for the next note to be read
                    chunk = ''
                
if __name__== "__main__":
        
    deid_date(sys.argv[1], sys.argv[2])
    