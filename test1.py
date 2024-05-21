def adjust_triggers(trigger_array):
    # Initialize variables
    n = len(trigger_array)
    if n == 0:
        return trigger_array
    
    # Create a copy of the array to store results
    result = trigger_array.copy()
    
    # Track the start index of the current group
    group_start = 0

    while group_start < n:
        # Find the end of the current group
        group_end = group_start
        while group_end < n and trigger_array[group_end] == trigger_array[group_start]:
            group_end += 1
        
        # Calculate the width of the current group
        group_width = group_end - group_start
        
        # If the width is less than 20, modify the values
        if group_width < 20:
            # If there is a previous group, use its value, otherwise use the next group's value
            if group_start > 0:
                previous_value = trigger_array[group_start - 1]
            elif group_end < n:
                previous_value = trigger_array[group_end]
            else:
                previous_value = trigger_array[group_start]  # edge case for single group array
            
            for i in range(group_start, group_end):
                result[i] = previous_value
        
        # Move to the next group
        group_start = group_end
    
    return result

# Example usage
trigger_array = [1, 1, 1, 2, 2, 3, 3, 3, 3, 3, 3, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 4, 4, 4]
adjusted_array = adjust_triggers(trigger_array)
print(adjusted_array)
