
def get_file_name_from_path(file_path):
    filename = file_path.split('/')[-1]
    return filename
      
def convert_eeg_events_to_list(events):
    output_list = []
    for row in events:
        action = row[0]
        start_time = row[1]
        end_time = row[2]
        start_index = row[3]
        end_index = row[4]
        duration = row[5]
        output_list.append(f"{action} ::: {start_time}  :::     {end_time} ::: {start_index} ::: {end_index} ::: {duration}")
    return output_list