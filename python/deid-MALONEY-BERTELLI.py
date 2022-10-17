# Aiden Maloney-Bertelli
# BMI 500 Lab 8
# Deidentifying location PHI

import re
import sys

phone_pattern = '(\d{3}[-\.\s/]??\d{3}[-\.\s/]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s/]??\d{4})'

# compiling the reg_ex would save sime time!
ph_reg = re.compile(phone_pattern)

# Phrases that precede locations
location_indicators = ["lives in", "resident of", "lived in", "lives at", "comes from", "called from", "visited from",
                       "arrived from", "returned to"]

employment_indicators_pre = ["employee of", "employed by", "employed at", "CEO of", "manager at", "manager for",
                             "manager of", "works at", "business"]

# Hospital indicators that follow hospital names
hospital_indicators = ["Hospital", "General Hospital", "Gen Hospital", "gen hosp", "hosp", "Medical Center",
                       "Med Center", "Med Ctr", "Rehab", "Clinic", "Rehabilitation", "Campus", "health center",
                       "cancer center", "development center", "community health center", "health and rehabilitation",
                       "Medical", "transferred to", "transferred from", "transfered to", "transfered from"]
hospital_file = r"/lists/stripped_hospitals.txt"
with open(hospital_file) as f:
    hospitals = f.read().upper().split("\n")


# Location indicators that follow locations
loc_indicators_suff = ["city", "town", "beach", "valley", "county", "harbor", "ville", "creek", "springs", "mountain",
                       "island", "lake", "lakes", "shore", "garden", "haven", "village", "grove", "hills", "hill",
                       "shire", "cove", "coast", "alley", "street", "terrace", "boulevard", "parkway", "highway",
                       "university", "college", "tower"]

# Location indicators that are most likely preceded by locations
loc_ind_suff_c = ["town", "ville", "harbor", "tower"]

# Location indicators that precede locations
# @loc_indicators_pre = ("cape", "fort", "lake", "mount", "santa", "los", "great","east","west","north","south");
loc_indicators_pre = ["cape", "fort", "lake", "mount", "santa", "los", "east", "west", "north", "south"]

apt_indicators = ["apt", "suite"]  # only check these after the street address is found
street_add_suff = ["park", "drive", "street", "road", "lane", "boulevard", "blvd", "avenue", "highway", "circle",
                    "ave", "place", "rd", "st"]

# Strict street address suffix: case-sensitive match on the following,
# and will be marked as PHI regardless of ambiguity (common words)
strict_street_add_suff = ["Park", "Drive", "Street", "Road", "Lane", "Boulevard", "Blvd", "Avenue", "Highway", "Ave",
                          "Rd", "PARK", "DRIVE", "STREET", "ROAD", "LANE", "BOULEVARD", "BLVD", "AVENUE", "HIGHWAY",
                          "AVE", "RD"]

universities_pre = ["University", "U", "Univ", "Univ."]

common_words_file = r"/dict/common_words.txt"
with open(common_words_file, 'r') as f:
    common_words_array = f.read().lower().split()
unambig_common_words_file = r"/dict/notes_common.txt"
with open(unambig_common_words_file, 'r') as f:
    unambig_common_words_array = f.read().lower().split()

us_states_abbre_file = r"/lists/us_states_abbre.txt"
more_us_state_abbreviations_file = r"/lists/more_us_state_abbreviations.txt"
with open(us_states_abbre_file) as f:
    us_state_abbre = f.read().upper().split()
with open(more_us_state_abbreviations_file) as f:
    us_state_abbre.append(f.read().upper().split())
us_states_file = r"/lists/us_states.txt"
with open(us_states_file) as f:
    us_states = f.read().upper().split("\n")

locations_unambig_file = r"/lists/locations_unambig.txt"
with open(locations_unambig_file) as f:
    locations_unambig = f.read().split("\n")
locations_ambig_file = r"/lists/locations_ambig.txt"
with open(locations_ambig_file) as f:
    locations_ambig = f.read().split("\n")

# store PHI that has been found
found_location_PHI = []

# The perl code handles texts a bit differently,
# we found that adding this offset to start and end positions would produce the same results
OFFSET = 27


def check_for_phone(patient, note, chunk, output_handle):
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
    output_handle.write('Patient {}\tNote {}\n'.format(patient, note))

    # search the whole chunk, and find every position that matches the regular expression
    # for each one write the results: "Start Start END"
    # Also for debugging purposes display on the screen (and don't write to file) 
    # the start, end and the actual personal information that we found
    for match in ph_reg.finditer(chunk):
        # debug print, 'end=" "' stops print() from adding a new line
        print(patient, note, end=' ')
        print((match.start() - offset), match.end() - offset, match.group())

        # create the string that we want to write to file ('start start end')
        result = str(match.start() - offset) + ' ' + str(match.start() - offset) + ' ' + str(match.end() - offset)

        # write the result to one line of output
        output_handle.write(result + '\n')


def deid_phone(text_path='id.text', output_path='phone.phi'):
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
    with open(output_path, 'w+') as output_file:
        with open(text_path) as text:
            # initilize an empty chunk. Go through the input file line by line
            # whenever we see the start_of_record pattern, note patient and note numbers and start 
            # adding everything to the 'chunk' until we see the end_of_record.
            chunk = ''
            for line in text:
                record_start = re.findall(start_of_record_pattern, line, flags=re.IGNORECASE)
                if len(record_start):
                    patient, note = record_start[0]
                chunk += line

                # check to see if we have seen the end of one note
                record_end = re.findall(end_of_record_pattern, line, flags=re.IGNORECASE)

                if len(record_end):
                    # Now we have a full patient note stored in `chunk`, along with patient numerb and note number
                    # pass all to check_for_phone to find any phone numbers in note.
                    check_for_phone(patient, note, chunk.strip(), output_file)

                    # initialize the chunk for the next note to be read
                    chunk = ''


def check_for_loc(patient, note, chunk, output_handle):
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
        Search the entire chunk for location occurances. Find the location of these occurances
        relative to the start of the chunk, and output these to the output_handle file.
        If there are no occurances, only output Patient X Note Y (X and Y are passed in as inputs) in one line.
    """
    # For each new note, the first line should be Patient X Note Y and then all the personal information positions
    output_handle.write('Patient {}\tNote {}\n'.format(patient, note))

    check_location_indicators(patient, note, chunk, output_handle)
    check_employment_indicators_pre(patient, note, chunk, output_handle)
    check_strict_address(patient, note, chunk, output_handle)
    check_non_strict_street_address(patient, note, chunk, output_handle)
    check_loc_indicators_suff(patient, note, chunk, output_handle)
    check_loc_ind_suff_c(patient, note, chunk, output_handle)
    #check_loc_indicators_pre(patient, note, chunk, output_handle)  # only catches false positives
    check_universities_pre(patient, note, chunk, output_handle)
    check_hospitals(patient, note, chunk, output_handle)
    check_unambig_loc(patient, note, chunk, output_handle)
    check_US_States(patient, note, chunk, output_handle)


def is_common(word):
    """
    Inputs:
        - word: word to check for commonness
    Logic:
        Return True if the word is identified as an ambiguous or unambiguous common word, regardless of case,
        and False otherwise
    """
    if word is None:
        return True
    return (word.strip().lower() in common_words_array) or (word.strip().lower() in unambig_common_words_array)


def is_unambig_common(word):
    """
    Inputs:
        - word: word to check for commonness
    Logic:
        Return True if the word is identified as an unambiguous common word, regardless of case, and False otherwise
    """
    if word is None:
        return True
    return (word.strip().lower() in unambig_common_words_array)


def is_US_State_Abbr(word):
    """
    Inputs:
        - word: word to check for whether it is a US state abbreviation
    Logic:
        Return True if the uppercase version of the word is a US state abbreviation and False otherwise
    """
    if word is None:
        return False
    return word.upper() in us_state_abbre


def is_US_State(word):
    """
    Inputs:
        - word: word to check for whether it is a US state name
    Logic:
        Return True if the uppercase version of the word is a US state and False otherwise
    """
    if word is None:
        return False
    return word.upper() in us_states


def check_location_indicators(patient, note, chunk, output_handle):
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
        Search the entire chunk for location indicators, such as "returned to" and mark the following word as a location
        if it is not a common word. Find the location of these occurances relative to the start of the chunk, and output
        these to the output_handle file.
    """
    for loc in location_indicators:
        loc_pattern = r'\b(' + loc + r')(\s+)([A-Za-z]+)\b'
        loc_reg = re.compile(loc_pattern, re.IGNORECASE)
        # search the whole chunk, and find every position that matches the regular expression
        # for each one write the results: "Start Start END"
        # Also for debugging purposes display on the screen (and don't write to file)
        # the start, end and the actual personal information that we found
        for match in loc_reg.finditer(chunk):
            if (not is_common(match.group(3))) or (match.group(3) in found_location_PHI):
                # add to lost of found location PHI
                if match.group(3) not in found_location_PHI:
                    found_location_PHI.append(match.group(3))

                # debug print, 'end=" "' stops print() from adding a new line
                print(patient, note, end=' ')
                print((match.start(3) - OFFSET), match.end(3) - OFFSET, match.group(3))

                # create the string that we want to write to file ('start start end')
                result = str(match.start(3) - OFFSET) + ' ' + str(match.start(3) - OFFSET) + ' ' + str(match.end(3) - OFFSET)

                # write the result to one line of output
                output_handle.write(result + '\n')


def check_employment_indicators_pre(patient, note, chunk, output_handle):
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
        Search the entire chunk for employment indicators, such as "employee of" and mark the following word as a location
        if it is not a common word. Find the location of these occurances relative to the start of the chunk, and output
        these to the output_handle file.
    """
    for employ_ind in employment_indicators_pre:
        employ_ind_pattern = r'\b(' + employ_ind + r')(\s+)([A-Za-z]+)\b'
        employ_ind_reg = re.compile(employ_ind_pattern, re.IGNORECASE)
        # search the whole chunk, and find every position that matches the regular expression
        # for each one write the results: "Start Start END"
        # Also for debugging purposes display on the screen (and don't write to file)
        # the start, end and the actual personal information that we found
        for match in employ_ind_reg.finditer(chunk):
            if (not is_common(match.group(3))) or (match.group(3) in found_location_PHI):
                # add to lost of found location PHI
                if match.group(3) not in found_location_PHI:
                    found_location_PHI.append(match.group(3))

                    # debug print, 'end=" "' stops print() from adding a new line
                    print(patient, note, end=' ')
                    print((match.start(3) - OFFSET), match.end(3) - OFFSET, match.group(3))

                    # create the string that we want to write to file ('start start end')
                    result = str(match.start(3) - OFFSET) + ' ' + str(match.start(3) - OFFSET) + ' ' + str(
                        match.end(3) - OFFSET)

                    # write the result to one line of output
                    output_handle.write(result + '\n')


def check_strict_address(patient, note, chunk, output_handle):
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
        Search the entire chunk for strict street address indicators and mark them as locations.
        Find the location of these occurances relative to the start of the chunk, and output
        these to the output_handle file.
    """
    for strict_add in strict_street_add_suff:
        strict_add_pattern = r'\b(([0-9]+ +)?(([A-Za-z\.\']+) +)?([A-Za-z\.\']+) +\b' + strict_add + r'\.?\b)\b'
        # want a case-sensitive search
        strict_add_reg = re.compile(strict_add_pattern)
        # search the whole chunk, and find every position that matches the regular expression
        # for each one write the results: "Start Start END"
        # Also for debugging purposes display on the screen (and don't write to file)
        # the start, end and the actual personal information that we found
        for match in strict_add_reg.finditer(chunk):
            # take the substring up to 30 characters after the found pattern
            if len(chunk) <= match.end() + 30:
                next_seg = chunk[match.end() + 1:len(chunk) - 1]
            else:
                next_seg = chunk[match.end() + 1:match.end() +30]
            end_of_add = match.end()
            # check for apartment or suite #
            for apt_ind in apt_indicators:
                apt_ind_pattern = r'\b(' + apt_ind + r'\.?\#? +[\w]+)\b'
                apt_ind_reg = re.compile(apt_ind_pattern, re.IGNORECASE)
                # just look for first match
                match2 = apt_ind_reg.search(next_seg)
                if match2 is not None:
                    end_of_add += match2.end() + 1
                    break
            if match.group(3) is None:
                if is_unambig_common(match.group(5)):
                    continue
            if is_unambig_common(match.group(4)) and is_unambig_common(match.group(5)):
                continue

            add_string = chunk[match.start():end_of_add]
            print(patient, note, end=' ')
            print((match.start() - OFFSET), end_of_add - OFFSET, add_string)

            # create the string that we want to write to file ('start start end')
            result = str(match.start() - OFFSET) + ' ' + str(match.start() - OFFSET) + ' ' + str(end_of_add - OFFSET)

            # write the result to one line of output
            output_handle.write(result + '\n')


def check_non_strict_street_address(patient, note, chunk, output_handle):
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
        Search the entire chunk for non-strict street address indicators and mark them as locations.
        Find the location of these occurances relative to the start of the chunk, and output
        these to the output_handle file.
    """
    for add in street_add_suff:
        add_pattern = r'\b(([0-9]+) +(([A-Za-z]+) +)?([A-Za-z]+) +' + add + r')\b'
        add_reg = re.compile(add_pattern, re.IGNORECASE)
        # search the whole chunk, and find every position that matches the regular expression
        # for each one write the results: "Start Start END"
        # Also for debugging purposes display on the screen (and don't write to file)
        # the start, end and the actual personal information that we found
        for match in add_reg.finditer(chunk):
            if match.group(3) is None or is_unambig_common(match.group(3)):
                continue
            if is_unambig_common(match.group(4)) or is_unambig_common(match.group(5)):
                continue
            # debug print, 'end=" "' stops print() from adding a new line
            print(patient, note, end=' ')
            print((match.start(3) - OFFSET), match.end(3) - OFFSET, match.group(3))

            # create the string that we want to write to file ('start start end')
            result = str(match.start(3) - OFFSET) + ' ' + str(match.start(3) - OFFSET) + ' ' + str(
            match.end(3) - OFFSET)

            # write the result to one line of output
            output_handle.write(result + '\n')


def check_loc_indicators_suff(patient, note, chunk, output_handle):
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
        Search the entire chunk for location suffixes, such as "city," and mark them with the preceding single words
        (if they are not common) as locations. Find the location of these occurances relative to the start of the chunk,
        and output these to the output_handle file.
    """
    for loc_suff in loc_indicators_suff:
        loc_suff_pattern = r'\b(([A-Za-z\-]+)? +)?(([A-Za-z\-]+) + *' + loc_suff + r'+)\b'
        loc_suff_reg = re.compile(loc_suff_pattern, re.IGNORECASE)
        # search the whole chunk, and find every position that matches the regular expression
        # for each one write the results: "Start Start END"
        # Also for debugging purposes display on the screen (and don't write to file)
        # the start, end and the actual personal information that we found
        for match in loc_suff_reg.finditer(chunk):
            if is_common(match.group(4)):
                continue
            # debug print, 'end=" "' stops print() from adding a new line
            print(patient, note, end=' ')
            print((match.start() - OFFSET), match.end() - OFFSET, match.group())

            # create the string that we want to write to file ('start start end')
            result = str(match.start() - OFFSET) + ' ' + str(match.start() - OFFSET) + ' ' + str(
                match.end() - OFFSET)

            # write the result to one line of output
            output_handle.write(result + '\n')


def check_loc_ind_suff_c(patient, note, chunk, output_handle):
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
        Search the entire chunk for location suffixes that are more common than those covered by
        check_loc_indicators_suff and mark them with the preceding words
        as locations. Find the location of these occurances relative to the start of the chunk,
        and output these to the output_handle file.
    """
    for loc_suff_c in loc_ind_suff_c:
        loc_suff_c_pattern = r'\b(([A-Za-z]+ +)?)(([A-Za-z]+)' + loc_suff_c + r'+)\b'
        loc_suff_c_reg = re.compile(loc_suff_c_pattern, re.IGNORECASE)
        # search the whole chunk, and find every position that matches the regular expression
        # for each one write the results: "Start Start END"
        # Also for debugging purposes display on the screen (and don't write to file)
        # the start, end and the actual personal information that we found
        for match in loc_suff_c_reg.finditer(chunk):
            if match.group(3) not in found_location_PHI:
                found_location_PHI.append(match.group(3))
            # debug print, 'end=" "' stops print() from adding a new line
            print(patient, note, end=' ')
            print((match.start(3) - OFFSET), match.end(3) - OFFSET, match.group(3))

            # create the string that we want to write to file ('start start end')
            result = str(match.start(3) - OFFSET) + ' ' + str(match.start(3) - OFFSET) + ' ' + str(
                match.end(3) - OFFSET)

            # write the result to one line of output
            output_handle.write(result + '\n')


def check_loc_indicators_pre(patient, note, chunk, output_handle):
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
        Search the entire chunk for location prefixes and mark them with the following words
        as locations. Find the location of these occurances relative to the start of the chunk,
        and output these to the output_handle file.
    """
    for loc_pre in loc_indicators_pre:
        loc_pre_pattern = r'\b(((' + loc_pre + r'+ *([A-Za-z\-]+)) *)([A-Za-z\-]+)?)\b'
        loc_pre_reg = re.compile(loc_pre_pattern, re.IGNORECASE)
        # search the whole chunk, and find every position that matches the regular expression
        # for each one write the results: "Start Start END"
        # Also for debugging purposes display on the screen (and don't write to file)
        # the start, end and the actual personal information that we found
        for match in loc_pre_reg.finditer(chunk):
            if is_common(match.group(4)) or is_common(match.group(5)):
                continue
            if match.group(3) is not None and match.group(3) not in found_location_PHI:
                found_location_PHI.append(match.group(3))

            # debug print, 'end=" "' stops print() from adding a new line
            print(patient, note, end=' ')
            print((match.start(3) - OFFSET), match.end(3) - OFFSET, match.group(3))

            # create the string that we want to write to file ('start start end')
            result = str(match.start(3) - OFFSET) + ' ' + str(match.start(3) - OFFSET) + ' ' + str(
                match.end(3) - OFFSET)

            # write the result to one line of output
            output_handle.write(result + '\n')


def check_universities_pre(patient, note, chunk, output_handle):
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
        Search the entire chunk for university prefixes, such as "University," and, if followed by a state or uncommon
        word, mark them with the preceding words as locations. Find the location of these occurances relative to the
        start of the chunk, and output these to the output_handle file.
    """
    for univ_pre in universities_pre:
        univ_pre_pattern = r'\b(((' + univ_pre + r'+of *([A-Za-z\-]+)) *)([A-Za-z\-]+)?)\b'
        univ_pre_reg = re.compile(univ_pre_pattern, re.IGNORECASE)
        # search the whole chunk, and find every position that matches the regular expression
        # for each one write the results: "Start Start END"
        # Also for debugging purposes display on the screen (and don't write to file)
        # the start, end and the actual personal information that we found
        for match in univ_pre_reg.finditer(chunk):
            if (not is_US_State(match.group(4))) and (not is_US_State_Abbr(match.group(4))) and is_common(match.group(4)):
                continue

            if match.group(3) is not None and match.group(3) not in found_location_PHI:
                found_location_PHI.append(match.group(3))

            # debug print, 'end=" "' stops print() from adding a new line
            print(patient, note, end=' ')
            print((match.start(3) - OFFSET), match.end(3) - OFFSET, match.group(3))

            # create the string that we want to write to file ('start start end')
            result = str(match.start(3) - OFFSET) + ' ' + str(match.start(3) - OFFSET) + ' ' + str(
                match.end(3) - OFFSET)

            # write the result to one line of output
            output_handle.write(result + '\n')

            if not is_common(match.group(5)):
                if match.group(5) is not None and match.group(5) not in found_location_PHI:
                    found_location_PHI.append(match.group(5))

                # debug print, 'end=" "' stops print() from adding a new line
                print(patient, note, end=' ')
                print((match.start(5) - OFFSET), match.end(5) - OFFSET, match.group(5))

                # create the string that we want to write to file ('start start end')
                result = str(match.start(5) - OFFSET) + ' ' + str(match.start(5) - OFFSET) + ' ' + str(
                    match.end(5) - OFFSET)

                # write the result to one line of output
                output_handle.write(result + '\n')


def check_hospitals(patient, note, chunk, output_handle):
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
        Search the entire chunk for known hospital names and mark them as locations.
        Find the location of these occurances relative to the start of the chunk,
        and output these to the output_handle file.
    """
    for hosp in hospitals:
        hosp_split = hosp.split()
        if len(hosp_split) == 0:
            continue
        hosp_pattern = r'\b(' + hosp_split[0] + ')'
        for i in range(1, len(hosp_split)):
            hosp_pattern += r'( )(' + hosp_split[i] + ')'
        hosp_pattern += r'\b'
        hosp_reg = re.compile(hosp_pattern, re.IGNORECASE)
        # search the whole chunk, and find every position that matches the regular expression
        # for each one write the results: "Start Start END"
        # Also for debugging purposes display on the screen (and don't write to file)
        # the start, end and the actual personal information that we found
        for match in hosp_reg.finditer(chunk):
            # debug print, 'end=" "' stops print() from adding a new line
            print(patient, note, end=' ')
            print((match.start() - OFFSET), match.end() - OFFSET, match.group())

            # create the string that we want to write to file ('start start end')
            result = str(match.start() - OFFSET) + ' ' + str(match.start() - OFFSET) + ' ' + str(match.end() - OFFSET)

            # write the result to one line of output
            output_handle.write(result + '\n')


def check_unambig_loc(patient, note, chunk, output_handle):
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
        Search the entire chunk for known, unambiguous locations and mark them
        as locations. Find the location of these occurances relative to the start of the chunk,
        and output these to the output_handle file.
    """
    for loc in locations_unambig:
        loc_split = loc.split()
        if len(loc_split) == 0:
            continue
        loc_pattern = r'\b(' + loc_split[0] + ')'
        for i in range(1, len(loc_split)):
            loc_pattern += r'( )(' + loc_split[i] + ')'
        loc_pattern += r'\b'
        loc_reg = re.compile(loc_pattern, re.IGNORECASE)
        # search the whole chunk, and find every position that matches the regular expression
        # for each one write the results: "Start Start END"
        # Also for debugging purposes display on the screen (and don't write to file)
        # the start, end and the actual personal information that we found
        for match in loc_reg.finditer(chunk):
            # debug print, 'end=" "' stops print() from adding a new line
            print(patient, note, end=' ')
            print((match.start() - OFFSET), match.end() - OFFSET, match.group())

            # create the string that we want to write to file ('start start end')
            result = str(match.start() - OFFSET) + ' ' + str(match.start() - OFFSET) + ' ' + str(match.end() - OFFSET)

            # write the result to one line of output
            output_handle.write(result + '\n')


def check_US_States(patient, note, chunk, output_handle):
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
        Search the entire chunk for US state names and mark them as locations. Find the location of these occurances
        relative to the start of the chunk, and output these to the output_handle file.
    """
    for state in us_states:
        state_split = state.split()
        if len(state_split) == 0:
            continue
        state_pattern = r'\b(' + state_split[0] + ')'
        for i in range(1, len(state_split)):
            state_pattern += r'( )(' + state_split[i] + ')'
        state_pattern += r'\b'
        state_reg = re.compile(state_pattern, re.IGNORECASE)
        # search the whole chunk, and find every position that matches the regular expression
        # for each one write the results: "Start Start END"
        # Also for debugging purposes display on the screen (and don't write to file)
        # the start, end and the actual personal information that we found
        for match in state_reg.finditer(chunk):
            # debug print, 'end=" "' stops print() from adding a new line
            print(patient, note, end=' ')
            print((match.start() - OFFSET), match.end() - OFFSET, match.group())

            # create the string that we want to write to file ('start start end')
            result = str(match.start() - OFFSET) + ' ' + str(match.start() - OFFSET) + ' ' + str(match.end() - OFFSET)

            # write the result to one line of output
            output_handle.write(result + '\n')


def deid_loc(text_path='id.text', output_path='location.phi'):
    """
    Inputs:
        - text_path: path to the file containing patient records
        - output_path: path to the output file.

    Outputs:
        for each patient note, the output file will start by a line declaring the note in the format of:
            Patient X Note Y
        then for each location found, it will have another line in the format of:
            start start end
        where the start is the start position of the detected location string, and end is the detected
        end position of the string both relative to the start of the patient note.
        If there is no location detected in the patient note, only the first line (Patient X Note Y) is printed
        to the output
    Screen Display:
        For each location detected, the following information will be displayed on the screen for debugging purposes
        (these will not be written to the output file):
            start end location
        where `start` is the start position of the detected location string, and `end` is the detected end position of the string
        both relative to the start of patient note.

    """
    # start of each note has the patter: START_OF_RECORD=PATIENT||||NOTE||||
    # where PATIENT is the patient number and NOTE is the note number.
    start_of_record_pattern = '^start_of_record=(\d+)\|\|\|\|(\d+)\|\|\|\|$'

    # end of each note has the patter: ||||END_OF_RECORD
    end_of_record_pattern = '\|\|\|\|END_OF_RECORD$'

    # open the output file just once to save time on the time intensive IO
    with open(output_path, 'w+') as output_file:
        with open(text_path) as text:
            # initilize an empty chunk. Go through the input file line by line
            # whenever we see the start_of_record pattern, note patient and note numbers and start
            # adding everything to the 'chunk' until we see the end_of_record.
            chunk = ''
            for line in text:
                record_start = re.findall(start_of_record_pattern, line, flags=re.IGNORECASE)
                if len(record_start):
                    patient, note = record_start[0]
                chunk += line

                # check to see if we have seen the end of one note
                record_end = re.findall(end_of_record_pattern, line, flags=re.IGNORECASE)

                if len(record_end):
                    # Now we have a full patient note stored in `chunk`, along with patient numerb and note number
                    # pass all to check_for_phone to find any phone numbers in note.
                    check_for_loc(patient, note, chunk.strip(), output_file)

                    # initialize the chunk for the next note to be read
                    chunk = ''


if __name__ == "__main__":

    # if len(sys.argv) > 1:
    #     deid_phone(sys.argv[1], sys.argv[2])
    # else:
    #     deid_phone()

    if len(sys.argv) > 1:
        deid_loc(sys.argv[1], sys.argv[2])
    else:
        deid_loc(text_path='id.text', output_path='location.phi')

