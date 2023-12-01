# Importing the necessary Python libraries
import yaml
from io import BytesIO
from PIL import Image
from base64 import b64decode
import openai
import gradio as gr



## OPENAI CONNECTION
## ---------------------------------------------------------------------------------------------------------------------
# Loading the API key and organization ID from file (NOT pushed to GitHub)
with open('../keys/openai-keys.yaml') as f:
    keys_yaml = yaml.safe_load(f)

# Applying our API key and organization ID to OpenAI
openai.organization = keys_yaml['ORG_ID']
openai.api_key = keys_yaml['API_KEY']



## GRADIO HELPER FUNCTIONS
## ---------------------------------------------------------------------------------------------------------------------
def generate_image(user_prompt):
    '''
    Generates an image using the DALL-E API per the user's prompt

    Inputs:
        - user_prompt (str): A body of text describing what the user would like to see

    Returns:
        - dalle_image (PIL): The image generated by DALL-E
    '''

    # Checking that the user prompt does not exceed 1000 characters
    if len(user_prompt) > 1000:
        raise gr.Error('Input prompt cannot exceed 1000 characters.')

    # Using DALL-E to generate the image as a base64 encoded object
    openai_response = openai.Image.create(
        prompt = user_prompt,
        n = 1,
        size = '1024x1024',
        response_format = 'b64_json'
    )

    # Decoding the base64 encoded object into a PIL image
    dalle_image = Image.open(BytesIO(b64decode(openai_response['data'][0]['b64_json'])))

    return dalle_image


## GRADIO UI LAYOUT & FUNCTIONALITY
## ---------------------------------------------------------------------------------------------------------------------
# Defining the building blocks that represent the form and function of the Gradio UI
with gr.Blocks(title = 'DALL-E Image Generator', theme = 'base') as image_generator:
    
    # Instantiating the UI interface
    header = gr.Markdown('''
    # DALL-E Image Generator
    
    Please enter a prompt for what you would like DALL-E to generate and click the "Generate Image" button to watch DALL-E work its magic!
    ''')
    user_prompt = gr.Textbox(label = 'What would you like to see?',
                             placeholder = 'Enter some text (up to 1000 characters) of what you would like DALL-E to generate.')
    generate_image_button = gr.Button('Generate Image')
    dalle_image = gr.Image(label = 'DALL-E Generated Image', interactive = False)

    # Defining the behavior for when the "Generate Image" button is clicked
    generate_image_button.click(fn = generate_image,
                                inputs = [user_prompt],
                                outputs = [dalle_image])




## SCRIPT INVOCATION
## ---------------------------------------------------------------------------------------------------------------------
if __name__ == "__main__":

    # Launching the Gradio UI
    image_generator.launch()