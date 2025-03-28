
import io
import os
import sys
import re
from openai import OpenAI
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
from dotenv import load_dotenv
load_dotenv()

model = "qwen2.5-coder:3b"
openai_key = os.environ["openai_key"]

qwen_llm = ChatOllama(
    model=model,
    num_gpu=1,
    num_cpu=0,
    # temperature=0,
    # other params...
)

client = OpenAI(
    api_key = openai_key
)

Chatgpt_llm = ChatOpenAI(model="gpt-4o",api_key=openai_key)

llm_dict={
    "qwen2.5-coder:3b": qwen_llm,
    "gpt-4o": Chatgpt_llm
}


def code_extraction(response: str):
    # Extract the text between ```python and ```
    pattern = re.compile(r"```python(.*?)```", re.DOTALL)
    match = pattern.search(response)

    if match:
        code_block = match.group(1).strip()
        return code_block
    else:
        return "No code block found."


file_location = "/mnt/cai-data/climate_agent/data/IBTrACS.NI.v04r01_new2.csv"
schema = '["storm" dtype="int64", "iso_time" dtype= object, "lat" dtype="float64", "lon" dtype="float64", "newdelhi_wind" dtype="float64", "newdelhi_pres" dtype="float64"]'

subbasin_unique = {
    "": "",
    "MM": "missing",
    "CS": "Caribbean Sea",
    "GM": "Gulf of Mexico",
    "CP": "Central Pacific",
    "BB": "Bay of Bengal",
    "AS": "Arabian Sea",
    "WA": "Western Australia",
    "EA": "Eastern Australia",
    "NA": "North Atlantic",  # North Atlantic is a basin not a subbasin
}
subbasin = "'Caribbean Sea','Gulf of Mexico','Central Pacific','Bay of Bengal','Arabian Sea','Western Australia','Eastern Australia','North Atlantic','missing'"
columns = [
    "storm",
    "lat",
    "lon",
    "newdelhi_wind",
    "newdelhi_pres",
    "subbasin",
    "season",
    "iso_time",
]
columns_desc = [
    "storm_id: datatype = int, desc = numeric id unique for each storm",
    "name: datatype = str, desc = Name of the storm. May be 'UNNAMED' if the storm was not named"
    "lattitude: datatype = float, desc = latitude",
    "longitude: datatype = float, desc = longitude",
    "wind_speed: datatype = float, desc = max sustained wind speed at that time in knots",
    "pressure: datatype = float, desc = minimum central pressure at that time in millibars(mb)",
    "season: datatype = int, desc = season number",
    "subbasin: datatype = str, desc =Either Arabian Sea or Bay of Bengal",
    "iso_time: datatype = str, desc = time of the storm in format YYYY-MM-DD HH:MM:SS",
    "landfall: datatype = float, desc =distance to landfall",
    "storm_grade: datatype = str, desc = D for Depression, DD for Deep Depression, CS for Cyclonic storm, SCS for Severe Cyclonic storm, VSCS for very severe cyclonic storm",
    "storm_speed: datatype = float, desc = translation speed of the storm",
]


def input_query(query: str):
    return f"""You are a data analysis agent, You are provided with the data on oceanic storms . Write a code to answer the user query based on the csv file present at the location: {file_location}, be careful with the file name, it should be exactly the same as the location. You will be provided with the schema of the data.Use pandas library to load and analysis the data. Format the code between strings "```python" and "```" Remember to print the result at the end of the code using print() function. Always print only the result e.g. print(6) not print(The largest windspeed is 6 mph).
    The data contains the following variable for the Northern Indian Ocean
    basin: The schema of the data is {columns_desc}.Keep in mind that each storm is represented using 360 rows. The iso_time, storm_grade, storm speed, wind speed, latitude, longitude vary over these 360 rows, but the name, season and storm_id remain constant for each unique storm. Therefor when asked for counting statistics of storms (for example the number of storms with wind speeds above a thereshold) only count the number of unique storm_ids and not the number of rows satisfying the condition. \nHere is the user's message: {query}"""



def code_executor(code: str) -> dict:
    """Execute python code"""
    generated_code = code
    # Create a StringIO buffer
    buffer = io.StringIO()

    # Redirect sys.stdout to the buffer
    sys.stdout = buffer
    try:
        buffer.seek(0)
        buffer.truncate(0)
        local_namespace = {}
        returned_code = generated_code
        exec(returned_code, {}, local_namespace)
        output = buffer.getvalue()
        return {
            "code_success": "Success",
            "output": output.replace("\n", ""),
            "code": returned_code,
        }
    except Exception as e:
        return {
            "code_success": "Failed",
            "output": f"Code execution failed ERROR {e}\ngenerated_code:\n{generated_code}",
            "code": returned_code,
        }


def run_app(message, model):
    llm = llm_dict.get(model,llm_dict["qwen2.5-coder:3b"])
    
    try:
        response = llm.invoke(input_query(message))
        # print("LLM Response:", response.content)

        extracted_code = code_extraction(response.content)
        # print("Extracted code:", extracted_code)

        output = code_executor(extracted_code)
        # print("Execution output:", output)

        return output
    except Exception as e:
        print("Error in run_app:", str(e))
        return {
            "code_success": "Failed",
            "output": f"Error processing request: {str(e)}",
            "code": "",
        }


if __name__ == "__main__":
    message = "Which storm has highest wind speed in 2003?"
    # Create a StringIO buffer

    run_app(message)
