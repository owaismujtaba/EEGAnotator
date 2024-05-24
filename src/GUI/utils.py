
def get_file_name_from_path(file_path):
    filename = file_path.split('/')[-1]
    return filename
      
def convert_lists_to_strings(input_list):
    output_list = []
    for sublist in input_list:
        action = sublist[0]
        start = sublist[1]
        end = sublist[2]
        duration = sublist[3]
        output_list.append(f"{action} ::: {start} ::: {end} ::: {duration}")
    return output_list