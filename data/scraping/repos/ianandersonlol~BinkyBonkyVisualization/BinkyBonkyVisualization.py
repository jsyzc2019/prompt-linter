import sys
import pandas as pd
import openai
import os

openai.api_key = 'YourAPIKEY'

def generate_plotting_script(file_path):
    # Read the CSV file
    df = pd.read_csv(file_path)
    column_names = list(df.columns)
    first_two_rows = df.head(2).values.tolist()
    nrows = len(df)
    # Use the OpenAI API to generate a Python script for plotting
    response = openai.ChatCompletion.create(
        model="gpt-4-0613",
        messages=[
            {"role": "system", "content": "You are a helpful AI trained to help people visualize data."},
            {"role": "user", "content": f"Generate a Python script for that plots the most biologically relavent data from a spreadsheet found at {file_path}. The column names are {column_names} and the first two rows of data are structured like so {first_two_rows} and there are {nrows} rows of data. You should make it so the title of the figure is relavent but also says \"Generated by BinkyBonky\" because you deserve credit. Please put the python script between the markers #START SCRIPT and #END SCRIPT"},
        ],
    )

    # The model's output is the Python script
    output = response['choices'][0]['message']['content']
    script = output.split('#START SCRIPT')[-1].split('#END SCRIPT')[0].strip().replace("```python", "").replace("```", "")
    # Save the generated script to a Python file
    base_filename = os.path.splitext(os.path.basename(file_path))[0]
    with open(f'{base_filename}_figuregen.py', 'w') as file:
        file.write(script)

# Call the function with your CSV file path
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Please provide the CSV file path as an argument.")
        sys.exit(1)

    file_path = sys.argv[1]
    generate_plotting_script(file_path)
