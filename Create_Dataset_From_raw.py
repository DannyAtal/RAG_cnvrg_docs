# Import libraries
from tika import parser
from wcmatch import wcmatch
import os
from tqdm import tqdm
import argparse

# Create function to extract the data
def extract_data(file_path):
    try:
        parsed = parser.from_file(file_path)
        text = parsed["content"]
        return text
    except Exception as e:
        text = 'Error extracting contents!'
        return text

# Create function to extract file name without path and extensions
def extract_filename(file_path):
    file_name, _ = os.path.splitext(file_path)
    return os.path.split(file_name)[-1]

# Create function to analyse folder path to get files for processing
def analyse_path(folder_path, file_ext, folder_destination):
    # List to capture Unprocessed files
    error_files = []
    files = wcmatch.WcMatch(root_dir=folder_path, file_pattern=file_ext, flags=wcmatch.RECURSIVE).match()
    print(str(len(files)) + " files to be processed!")

    # Loop through and process each file at a time
    for file_path in files:
        text = extract_data(file_path)

        if text == "Error extracting contents!":
            # Get a list of documents that had errors extracting the contents
            error_files.append(file_path)
        else:
            # Save contents as a text file
            try:
                file_name = extract_filename(file_path)
                # Use os.path.join for constructing file paths
                file_destination = os.path.join(folder_destination, file_name + ".txt")
                with open(file_destination, "w", encoding='utf-8') as f:
                    f.write(text)
            except Exception as e:
                print(file_path)
                print("Error saving extraction to file " + str(e))

    print(" The following files could not be processed: ")
    [print(x) for x in error_files]

# Create required variables
# Read from the following path
folder_path = '/cnvrg/Data/'
# Only process the following file formats
file_ext = "*.doc|*.docx|*.xlsx|*.xls|*.pdf|*.txt|*.ppt|*.pptx|*.md"
# Save to the following path
folder_destination = '/cnvrg/Data/'

# Run the extraction program
analyse_path(folder_path, file_ext, folder_destination)

def extract_sentences(file_path):
    # This is what will be returned from the function with Empty as a placeholder
    final_content = "Empty"
    # The files contents will be saved in the variable below for processing
    content = ''
    # Stride length is the maximum number of words we want to include in our sequence being generated
    stride = 500

    # Validate file path and return "Empty" if not valid
    if not os.path.isfile(file_path):
        print("{} does not exist ".format(file_path))
        return final_content

    # Read file and remove empty line and new lines
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file.readlines():
            if line.strip():
                if len(line.strip()) > 2:
                    content += line.replace('\n', '')

    # Create list of words and generate number of words
    split_content = content.split()
    seq_len = len(split_content)

    # Check that contents have been extracted and reset Empty flag
    if seq_len > 0:
        final_content = ""

    # Create the sequences
    for begin_loc in tqdm(range(0, seq_len, stride)):
        end_loc = min(begin_loc + stride, seq_len)
        if len(split_content[begin_loc:end_loc]) != 0:
            # Include a new line at the end of the generated sequence
            final_content += "<s>" + ' '.join(split_content[begin_loc:end_loc]) + "</s> \n"

    # Return the sequences
    return final_content

def create_dataset(folder_path, file_ext, folder_destination, dataset_name="dataset.txt"):
    # folder_path is the source path
    # file_ext is the file formats to be matched
    # folder_destination is where to save the dataset
    # dataset_name is the name of the dataset (default will be dataset.txt)

    # Save file paths matched in files variable
    print("Start processing ...")
    files = wcmatch.WcMatch(root_dir=folder_path, file_pattern=file_ext, flags=wcmatch.RECURSIVE).match()
    print(str(len(files)) + " files to be processed!")

    # Loop through and process each file
    for file_path in files:
        try:
            # Get extracted sentences
            contents = extract_sentences(file_path)
            # Ignore "Empty" sentences
            if contents != 'Empty':
                # Use os.path.join for constructing file paths
                file_destination = os.path.join(folder_destination, dataset_name)
                with open(file_destination, "a", encoding='utf-8') as f:
                    f.write(contents)
        except Exception as e:
            # Log any issues encountered for further investigation
            print(file_path)
            print("Error saving extraction to file " + str(e))

    print("Finished processing ...")

# Read from the following path
folder_path = '/cnvrg/Data/'
# Only process the following file formats
file_ext = "*.txt"
# Save to the following path
folder_destination = '/cnvrg/Data/'
# Dataset name (can be omitted to use default values)
dataset_name = '/cnvrg/Data/cnvrg_embedding_dataset.txt'

create_dataset(folder_path, file_ext, folder_destination, dataset_name)
