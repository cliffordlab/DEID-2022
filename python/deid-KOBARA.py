import re
import sys





'''
this is just experiment
ref = ["Memorial hospital", "MA"]
pattern = "|".join(ref)
reg = re.compile(pattern, re.IGNORECASE)
check_chunk = "I went to the Memorial hospital in memorial day"
for match in re.findall(reg, check_chunk):
    print(match)
'''

'''
python deid-KOBARA.py id.text loc.phi 
python stats.py id.deid id-phi.phrase loc.phi     
 
'''







# Prepare a location list from known name of locations and hospitals
# from known hospital list
with open('../lists/stripped_hospitals.txt') as hosp:
    hosp_list = list()
    for name in hosp:
        name_ = name.replace('\n','')
        hosp_list = hosp_list + [name_]

# from known ambiguous local place names 
with open('../lists/local_places_ambig.txt') as local_am:
    local_am_list = list()
    for name in local_am:
        name_ = name.replace('\n','')
        local_am_list = local_am_list + [name_]

# from known local places
with open('../lists/local_places_unambig.txt') as local_unam:
    local_unam_list = list()
    for name in local_unam:
        name_ = name.replace('\n','')
        local_unam_list = local_unam_list + [name_]

# from known ambiguous locations name
with open('../lists/locations_ambig.txt') as loc_am:
    loc_am_list = list()
    # In this text file the first line is blank
    # Need to read lines except the 1st line
    text = loc_am.readlines()
    length = len(text) 
    for i in range(1, length-1):
        name_ = text[i]
        name = name_.replace('\n','')
        loc_am_list = loc_am_list + [name]

# from known locations name 
with open('../lists/locations_unambig.txt') as loc_unam:
    loc_unam_list = list()
    for name in loc_unam:
        name_ = name.replace('\n','')
        loc_unam_list = loc_unam_list + [name_]

# Total list of words that can capture the location names
total_strings = hosp_list + local_am_list + local_unam_list + loc_am_list + loc_unam_list 
loc_pattern = "|".join(total_strings)
ph_reg = re.compile(loc_pattern, re.IGNORECASE)


#phone_pattern ='(\d{3}[-\.\s/]??\d{3}[-\.\s/]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s/]??\d{4})'
#ph_reg = re.compile(phone_pattern)


def check_for_location(patient, note, chunk, output_handle):

    offset = 27
    output_handle.write('Patient {}\tNote {}\n'.format(patient,note))

    
    for match in re.finditer(ph_reg, chunk):
                
            # debug print, 'end=" "' stops print() from adding a new line
            print(patient, note, end=' ')
            print((match.start()-offset),match.end()-offset, match.group())
                
            # create the string that we want to write to file ('start start end')    
            result = str(match.start()-offset) + ' ' + str(match.start()-offset) +' '+ str(match.end()-offset) 
            
            # write the result to one line of output
            output_handle.write(result+'\n')

            
def deid_location(text_path= 'id.text', output_path = 'loc.phi'):
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
                    check_for_location(patient,note,chunk.strip(), output_file)
                    
                    # initialize the chunk for the next note to be read
                    chunk = ''
                
if __name__== "__main__":
        
    
    
    deid_location(sys.argv[1], sys.argv[2])
    
