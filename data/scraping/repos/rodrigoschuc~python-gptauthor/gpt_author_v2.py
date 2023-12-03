# -*- coding: utf-8 -*-
"""gpt-author-v2

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1dJ_WQ_4OTm2F6e6hpqVc6CUCW_jBNHMd

# gpt-author v2
By Matt Shumer (https://twitter.com/mattshumer_)

Github repo: https://github.com/mshumer/gpt-author

Generate an entire novel in minutes, and automatically package it as an e-book.

To generate a book:
1.  In the first cell, add in your OpenAI, Stability, and (optionally, Anthropic) keys (see the first cell for instructions to get them).
2.  Fill in the prompt, number of chapters, and writing style in the last cell.
3. Run all the cells! After some time, your EPUB file should appear in the filesystem.
"""

!pip install openai
!pip install EbookLib
!pip install anthropic

from openai import OpenAI

client = OpenAI(api_key="YOUR OPENAI KEY")
import os
from ebooklib import epub
import base64
import os
import requests

 # get it at https://platform.openai.com/
stability_api_key = "YOUR STABILITY KEY" # get it at https://beta.dreamstudio.ai/
anthropic_api_key = "YOUR ANTHROPIC API KEY" # optional, if you don't add it, keep it as "YOUR ANTHROPIC API KEY"

if anthropic_api_key != "YOUR ANTHROPIC API KEY":
  claude_true = True
else:
  claude_true = False

def generate_cover_prompt(plot):
    response = client.chat.completions.create(model="gpt-3.5-turbo-16k",
    messages=[
        {"role": "system", "content": "You are a creative assistant that writes a spec for the cover art of a book, based on the book's plot."},
        {"role": "user", "content": f"Plot: {plot}\n\n--\n\nDescribe the cover we should create, based on the plot. This should be two sentences long, maximum."}
    ])
    return response['choices'][0]['message']['content']


def create_cover_image(plot):

  plot = str(generate_cover_prompt(plot))

  engine_id = "stable-diffusion-xl-beta-v2-2-2"
  api_host = os.getenv('API_HOST', 'https://api.stability.ai')
  api_key = stability_api_key

  if api_key is None:
      raise Exception("Missing Stability API key.")

  response = requests.post(
      f"{api_host}/v1/generation/{engine_id}/text-to-image",
      headers={
          "Content-Type": "application/json",
          "Accept": "application/json",
          "Authorization": f"Bearer {api_key}"
      },
      json={
          "text_prompts": [
              {
                  "text": plot
              }
          ],
          "cfg_scale": 7,
          "clip_guidance_preset": "FAST_BLUE",
          "height": 768,
          "width": 512,
          "samples": 1,
          "steps": 30,
      },
  )

  if response.status_code != 200:
      raise Exception("Non-200 response: " + str(response.text))

  data = response.json()

  for i, image in enumerate(data["artifacts"]):
      with open(f"/content/cover.png", "wb") as f: # replace this if running locally, to where you store the cover file
          f.write(base64.b64decode(image["base64"]))

def create_epub(title, author, chapters, cover_image_path='cover.png'):
    book = epub.EpubBook()

    # Set metadata
    book.set_identifier('id123456')
    book.set_title(title)
    book.set_language('en')
    book.add_author(author)

    # Add cover image
    with open(cover_image_path, 'rb') as cover_file:
        cover_image = cover_file.read()
    book.set_cover('cover.png', cover_image)

    # Create chapters and add them to the book
    epub_chapters = []
    for i, chapter_dict in enumerate(chapters):
        full_chapter_title = list(chapter_dict.keys())[0]
        chapter_content = list(chapter_dict.values())[0]
        if ' - ' in full_chapter_title:
            chapter_title = full_chapter_title.split(' - ')[1]
        else:
            chapter_title = full_chapter_title

        chapter_file_name = f'chapter_{i+1}.xhtml'
        epub_chapter = epub.EpubHtml(title=chapter_title, file_name=chapter_file_name, lang='en')

        # Add paragraph breaks
        formatted_content = ''.join(f'<p>{paragraph.strip()}</p>' for paragraph in chapter_content.split('\n') if paragraph.strip())

        epub_chapter.content = f'<h1>{chapter_title}</h1>{formatted_content}'
        book.add_item(epub_chapter)
        epub_chapters.append(epub_chapter)


    # Define Table of Contents
    book.toc = (epub_chapters)

    # Add default NCX and Nav files
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    # Define CSS style
    style = '''
    @namespace epub "http://www.idpf.org/2007/ops";
    body {
        font-family: Cambria, Liberation Serif, serif;
    }
    h1 {
        text-align: left;
        text-transform: uppercase;
        font-weight: 200;
    }
    '''

    # Add CSS file
    nav_css = epub.EpubItem(uid="style_nav", file_name="style/nav.css", media_type="text/css", content=style)
    book.add_item(nav_css)

    # Create spine
    book.spine = ['nav'] + epub_chapters

    # Save the EPUB file
    epub.write_epub(f'{title}.epub', book)

from openai import OpenAI

client = OpenAI(api_key="YOUR OPENAI KEY")
import random
import json
import ast
from anthropic import Anthropic

def print_step_costs(response, model):
  input = response['usage']['prompt_tokens']
  output = response['usage']['completion_tokens']

  if model == "gpt-4" or model == "gpt-4":
    input_per_token = 0.00003
    output_per_token = 0.00006
  if model == "gpt-3.5-turbo-16k":
    input_per_token = 0.000003
    output_per_token = 0.000004
  if model == "gpt-4-32k" or model == "gpt-4-32k":
    input_per_token = 0.00006
    output_per_token = 0.00012
  if model == "gpt-3.5-turbo" or model == "gpt-3.5-turbo":
    input_per_token = 0.0000015
    output_per_token = 0.000002
  if model == "claude-2":
    input_per_token = 0.00001102
    output_per_token = 0.00003268

  input_cost = int(input) * input_per_token
  output_cost = int(output) * output_per_token

  total_cost = input_cost + output_cost
  print('Step Cost (OpenAI):', total_cost)

def print_step_costs_anthropic(prompt, response):
  client = Anthropic()
  in_tokens = client.count_tokens(prompt)
  out_tokens = client.count_tokens(response)

  input_cost = 0.00001102 * in_tokens
  output_cost = 0.00003268 * out_tokens

  total_cost = input_cost + output_cost
  print('Step Cost (Anthropic):', total_cost)

def generate_plots(prompt):
    response = client.chat.completions.create(model="gpt-4",
    messages=[
        {"role": "system", "content": "You are a creative assistant that generates engaging fantasy novel plots."},
        {"role": "user", "content": f"Generate 10 fantasy novel plots based on this prompt: {prompt}"}
    ])

    print_step_costs(response, "gpt-4")

    return response['choices'][0]['message']['content'].split('\n')

def select_most_engaging(plots):
    response = client.chat.completions.create(model="gpt-4",
    messages=[
        {"role": "system", "content": "You are an expert in writing fantastic fantasy novel plots."},
        {"role": "user", "content": f"Here are a number of possible plots for a new novel: {plots}\n\n--\n\nNow, write the final plot that we will go with. It can be one of these, a mix of the best elements of multiple, or something completely new and better. The most important thing is the plot should be fantastic, unique, and engaging."}
    ])

    print_step_costs(response, "gpt-4")

    return response['choices'][0]['message']['content']

def improve_plot(plot):
    response = client.chat.completions.create(model="gpt-4",
    messages=[
        {"role": "system", "content": "You are an expert in improving and refining story plots."},
        {"role": "user", "content": f"Improve this plot: {plot}"}
    ])

    print_step_costs(response, "gpt-4")

    return response['choices'][0]['message']['content']

def get_title(plot):
    response = client.chat.completions.create(model="gpt-3.5-turbo-16k",
    messages=[
        {"role": "system", "content": "You are an expert writer."},
        {"role": "user", "content": f"Here is the plot: {plot}\n\nWhat is the title of this book? Just respond with the title, do nothing else."}
    ])

    print_step_costs(response, "gpt-3.5-turbo-16k")

    return response['choices'][0]['message']['content']

def write_first_chapter(plot, first_chapter_title, writing_style, claude=True):
    if claude:
      url = "https://api.anthropic.com/v1/complete"

      headers = {
          "anthropic-version": "2023-06-01",
          "content-type": "application/json",
          "x-api-key": anthropic_api_key,
      }

      prompt_one = f"\n\nHuman: You are a world-class fantasy writer. I will give you the title of a novel, a high-level plot to follow, and a desired writing style to use. From the title, plot, and writing style, write the first chapter of the novel. Make it incredibly unique, engaging, and well-written. Start it off with a bang, and include dialogue. Include only the chapter text, and no surrounding explanations or text. Do you understand?\n\nAssistant: Yes, I understand. Please provide the title, plot, and writing style, and I will write a fantastic opening chapter with dialogue that will hook the reader.\n\nHuman: Here is the high-level plot to follow: {plot}\n\The title of the novel is: `{first_chapter_title}`.\n\nHere is a description of the writing style you should use: `{writing_style}`\n\nWrite the first chapter please!\n\nAssistant: Okay, I've got a really exciting first chapter for you. It's twenty paragraphs long and very well-written. As you can see, the language I use is very understandable — I avoided using overly complex words and phrases:\n\nTitle: {first_chapter_title}\n\nChapter #1 Text```"

      data = {
      "model": "claude-2",
      "prompt": prompt_one,
      "max_tokens_to_sample": 5000,
      }

      response = requests.post(url, headers=headers, json=data)

      initial_first_chapter = response.json()['completion'].strip().split('```')[0].strip()

      print_step_costs_anthropic(prompt_one, response.json()['completion'])

      prompt_two = f"\n\nHuman: You are a world-class fantasy writer. Your job is to take your student's rough initial draft of the first chapter of their fantasy novel, and rewrite it to be significantly better, with much more detail. Do you understand?\n\nAssistant: Yes, I understand. Please provide the plot and the student-written chapter, and I will rewrite the chapter in a far superior way.\n\nHuman: Here is the high-level plot you asked your student to follow: {plot}\n\nHere is the first chapter they wrote: {initial_first_chapter}\n\nNow, rewrite the first chapter of this novel, in a way that is far superior to your student's chapter. It should still follow the exact same plot, but it should be far more detailed, much longer, and more engaging. Here is a description of the writing style you should use: `{writing_style}`\n\nAssistant: Okay, I've rewritten the first chapter. I took great care to improve it. While the plot is the same, you can see that my version is noticeably longer, easier to read, and more exciting. Also, the language I used is far more accessible to a broader audience.\n\n```"
      data = {
      "model": "claude-2",
      "prompt": prompt_two,
      "max_tokens_to_sample": 5000,
      }

      response_improved = requests.post(url, headers=headers, json=data)

      print_step_costs_anthropic(prompt_two, response_improved.json()['completion'])

      return response_improved.json()['completion'].strip().split('```')[0].strip()


    else:
      response = client.chat.completions.create(model="gpt-4",
      messages=[
          {"role": "system", "content": "You are a world-class fantasy writer."},
          {"role": "user", "content": f"Here is the high-level plot to follow: {plot}\n\nWrite the first chapter of this novel: `{first_chapter_title}`.\n\nMake it incredibly unique, engaging, and well-written.\n\nHere is a description of the writing style you should use: `{writing_style}`\n\nInclude only the chapter text. There is no need to rewrite the chapter name."}
      ])

      print_step_costs(response, "gpt-4")

      improved_response = client.chat.completions.create(model="gpt-4-32k",
      messages=[
          {"role": "system", "content": "You are a world-class fantasy writer. Your job is to take your student's rough initial draft of the first chapter of their fantasy novel, and rewrite it to be significantly better, with much more detail."},
          {"role": "user", "content": f"Here is the high-level plot you asked your student to follow: {plot}\n\nHere is the first chapter they wrote: {response['choices'][0]['message']['content']}\n\nNow, rewrite the first chapter of this novel, in a way that is far superior to your student's chapter. It should still follow the exact same plot, but it should be far more detailed, much longer, and more engaging. Here is a description of the writing style you should use: `{writing_style}`"}
      ])

      print_step_costs(response, "gpt-4-32k")

      return improved_response['choices'][0]['message']['content']


def write_chapter(previous_chapters, plot, chapter_title, claude=True):
    if claude:
        url = "https://api.anthropic.com/v1/complete"

        headers = {
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
            "x-api-key": anthropic_api_key,
        }

        prompt = f"\n\nHuman: You are a world-class fantasy writer. I will provide you with the plot of the novel, the previous chapters, and the plan for the next chapter. Your task is to write the next chapter of the novel, following the plot and taking in the previous chapters as context. Do you understand?\n\nAssistant: Yes, I understand. You want me to write the next chapter of a novel, using the plot you provide, the previous chapters for context, and a specific plan for the next chapter. I will ensure the chapter is beautifully written and I will not rewrite the chapter name.\n\nHuman: That's correct. Here is the plot: {plot}\n\nHere are the previous chapters: {previous_chapters}\n\nHere is the plan for the next chapter: {chapter_title}\n\nWrite it beautifully. Include only the chapter text. There is no need to rewrite the chapter name.\n\nAssistant: Here is the next chapter. As you can see, it's around the same length as the previous chapters, and contains witty dialogue:\n```Chapter"

        data = {
            "model": "claude-2",
            "prompt": prompt,
            "max_tokens_to_sample": 5000,
        }

        response = requests.post(url, headers=headers, json=data)

        print_step_costs_anthropic(prompt, response.json()['completion'])

        return 'Chapter ' + response.json()['completion'].strip().split('```')[0].strip()
    else:
        try:
            i = random.randint(1,2242)
            response = client.chat.completions.create(model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a world-class fantasy writer."},
                {"role": "user", "content": f"Plot: {plot}, Previous Chapters: {previous_chapters}\n\n--\n\nWrite the next chapter of this novel, following the plot and taking in the previous chapters as context. Here is the plan for this chapter: {chapter_title}\n\nWrite it beautifully. Include only the chapter text. There is no need to rewrite the chapter name."}
            ])

            print_step_costs(response, "gpt-4")

            return response['choices'][0]['message']['content']
        except:
            response = client.chat.completions.create(model="gpt-4-32k",
            messages=[
                {"role": "system", "content": "You are a world-class fantasy writer."},
                {"role": "user", "content": f"Plot: {plot}, Previous Chapters: {previous_chapters}\n\n--\n\nWrite the next chapter of this novel, following the plot and taking in the previous chapters as context. Here is the plan for this chapter: {chapter_title}\n\nWrite it beautifully. Include only the chapter text. There is no need to rewrite the chapter name."}
            ])

            print_step_costs(response, "gpt-4-32k")

            return response['choices'][0]['message']['content']


def generate_storyline(prompt, num_chapters):
    print("Generating storyline with chapters and high-level details...")
    json_format = """[{"Chapter CHAPTER_NUMBER_HERE - CHAPTER_TITLE_GOES_HERE": "CHAPTER_OVERVIEW_AND_DETAILS_GOES_HERE"}, ...]"""
    response = client.chat.completions.create(model="gpt-4",
    messages=[
        {"role": "system", "content": "You are a world-class fantasy writer. Your job is to write a detailed storyline, complete with chapters, for a fantasy novel. Don't be flowery -- you want to get the message across in as few words as possible. But those words should contain lots of information."},
        {"role": "user", "content": f'Write a fantastic storyline with {num_chapters} chapters and high-level details based on this plot: {prompt}.\n\nDo it in this list of dictionaries format {json_format}'}
    ])

    print_step_costs(response, "gpt-4")

    improved_response = client.chat.completions.create(model="gpt-4",
    messages=[
        {"role": "system", "content": "You are a world-class fantasy writer. Your job is to take your student's rough initial draft of the storyline of a fantasy novel, and rewrite it to be significantly better."},
        {"role": "user", "content": f"Here is the draft storyline they wrote: {response['choices'][0]['message']['content']}\n\nNow, rewrite the storyline, in a way that is far superior to your student's version. It should have the same number of chapters, but it should be much improved in as many ways as possible. Remember to do it in this list of dictionaries format {json_format}"}
    ])

    print_step_costs(improved_response, "gpt-4")

    return improved_response['choices'][0]['message']['content']


def write_to_file(prompt, content):

    # Create a directory for the prompts if it doesn't exist
    if not os.path.exists('prompts'):
        os.mkdir('prompts')

    # Replace invalid characters for filenames
    valid_filename = ''.join(c for c in prompt if c.isalnum() or c in (' ', '.', '_')).rstrip()
    file_path = f'prompts/{valid_filename}.txt'

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f'Output for prompt "{prompt}" has been written to {file_path}\n')


def write_fantasy_novel(prompt, num_chapters, writing_style, claude_true=False):
    plots = generate_plots(prompt)
    print('generated plots')

    best_plot = select_most_engaging(plots)
    print('selected best plot')

    improved_plot = improve_plot(best_plot)
    print('plot improved')

    title = get_title(improved_plot)
    print('title generated')

    storyline = generate_storyline(improved_plot, num_chapters)
    print('storyline generated')
    chapter_titles = ast.literal_eval(storyline)


    novel = f"Storyline:\n{storyline}\n\n"

    first_chapter = write_first_chapter(storyline, chapter_titles[0], writing_style.strip(), claude_true)
    print('first chapter written')
    novel += f"Chapter 1:\n{first_chapter}\n"
    chapters = [first_chapter]

    for i in range(num_chapters - 1):
        print(f"Writing chapter {i+2}...") # + 2 because the first chapter was already added

        chapter = write_chapter(novel, storyline, chapter_titles[i+1])
        try:
          if len(str(chapter)) < 100:
            print('Length minimum not hit. Trying again.')
            chapter = write_chapter(novel, storyline, chapter_titles[i+1])
        except:
          chapter = write_chapter(novel, storyline, chapter_titles[i+1])

        novel += f"Chapter {i+2}:\n{chapter}\n"
        chapters.append(chapter)

    return novel, title, chapters, chapter_titles

# Example usage:
prompt = "A kingdom hidden deep in the forest, where every tree is a portal to another world."
num_chapters = 10
writing_style = "Clear and easily understandable, similar to a young adult novel. Lots of dialogue."
novel, title, chapters, chapter_titles = write_fantasy_novel(prompt, num_chapters, writing_style, claude_true)

# Replace chapter descriptions with body text in chapter_titles
for i, chapter in enumerate(chapters):
    chapter_number_and_title = list(chapter_titles[i].keys())[0]
    chapter_titles[i] = {chapter_number_and_title: chapter}

# Create the cover
create_cover_image(str(chapter_titles))

# Create the EPUB file
create_epub(title, 'AI', chapter_titles, '/content/cover.png')