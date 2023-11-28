import re
import os
import matplotlib

# Use a different backend that supports interactive plotting
# matplotlib.use('TkAgg')

import matplotlib.pyplot as plt

def extract_values(file_path):
    # Define the pattern using regular expression
    pattern = r'AZ: ([-+]?\d*\.\d+|\d+), MCTS: ([-+]?\d*\.\d+|\d+), AZ avg/([-+]?\d*\.\d+|\d+): ([-+]?\d*\.\d+|\d+)'

    # Open the file and read its content
    with open(file_path, 'r') as file:
        content = file.read()

    # Use re.findall to find all occurrences of the pattern
    matches = re.findall(pattern, content)

    # Extract the values of x from the matches
    x_values = [float(match[3])  for match in matches]

    return x_values

# Specify the path to your text file
experiment = "test_ttt_setting/log-evaluator-0.txt"

file_path = f'./open_spiel/results/{experiment}'
base_name_without_extension = os.path.splitext(os.path.basename(file_path))[0]

# Call the function and get the extracted values
result = extract_values(file_path)

# Print the result
print("Extracted values of x:", result)

# Plot the extracted values
plt.plot(result, marker='o', linestyle='-', color='b')
plt.title('Extracted Values of x')
plt.xlabel('Index')
plt.ylabel('Value of x')
plt.grid(True)
plt.savefig(base_name_without_extension + '.png')
plt.show()