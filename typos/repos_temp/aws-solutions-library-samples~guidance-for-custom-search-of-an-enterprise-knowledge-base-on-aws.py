"""Use the following pieces of context to answer the question at the end. If you don't know the answer, just say that you don't know, don't try to make up an answer.

{context}

Question: {question}
Helpful Answer:""""""Use the following pieces of context to answer the users question. 
If you don't know the answer, just say that you don't know, don't try to make up an answer.
----------------
{context}""""""Use the following portion of a long document to see if any of the text is relevant to answer the question. 
Return any relevant text verbatim.
{context}
Question: {question}
Relevant text, if any:""""""Given the following extracted parts of a long document and a question, create a final answer with references ("SOURCES"). 
If you don't know the answer, just say that you don't know. Don't try to make up an answer.
ALWAYS return a "SOURCES" part in your answer.

QUESTION: Which state/country's law governs the interpretation of the contract?
=========
Content: This Agreement is governed by English law and the parties submit to the exclusive jurisdiction of the English courts in  relation to any dispute (contractual or non-contractual) concerning this Agreement save that either party may apply to any court for an  injunction or other relief to protect its Intellectual Property Rights.
Source: 28-pl
Content: No Waiver. Failure or delay in exercising any right or remedy under this Agreement shall not constitute a waiver of such (or any other)  right or remedy.\n\n11.7 Severability. The invalidity, illegality or unenforceability of any term (or part of a term) of this Agreement shall not affect the continuation  in force of the remainder of the term (if any) and this Agreement.\n\n11.8 No Agency. Except as expressly stated otherwise, nothing in this Agreement shall create an agency, partnership or joint venture of any  kind between the parties.\n\n11.9 No Third-Party Beneficiaries.
Source: 30-pl
Content: (b) if Google believes, in good faith, that the Distributor has violated or caused Google to violate any Anti-Bribery Laws (as  defined in Clause 8.5) or that such a violation is reasonably likely to occur,
Source: 4-pl
=========
FINAL ANSWER: This Agreement is governed by English law.
SOURCES: 28-pl

QUESTION: What did the president say about Michael Jackson?
=========
Content: Madam Speaker, Madam Vice President, our First Lady and Second Gentleman. Members of Congress and the Cabinet. Justices of the Supreme Court. My fellow Americans.  \n\nLast year COVID-19 kept us apart. This year we are finally together again. \n\nTonight, we meet as Democrats Republicans and Independents. But most importantly as Americans. \n\nWith a duty to one another to the American people to the Constitution. \n\nAnd with an unwavering resolve that freedom will always triumph over tyranny. \n\nSix days ago, Russia’s Vladimir Putin sought to shake the foundations of the free world thinking he could make it bend to his menacing ways. But he badly miscalculated. \n\nHe thought he could roll into Ukraine and the world would roll over. Instead he met a wall of strength he never imagined. \n\nHe met the Ukrainian people. \n\nFrom President Zelenskyy to every Ukrainian, their fearlessness, their courage, their determination, inspires the world. \n\nGroups of citizens blocking tanks with their bodies. Everyone from students to retirees teachers turned soldiers defending their homeland.
Source: 0-pl
Content: And we won’t stop. \n\nWe have lost so much to COVID-19. Time with one another. And worst of all, so much loss of life. \n\nLet’s use this moment to reset. Let’s stop looking at COVID-19 as a partisan dividing line and see it for what it is: A God-awful disease.  \n\nLet’s stop seeing each other as enemies, and start seeing each other for who we really are: Fellow Americans.  \n\nWe can’t change how divided we’ve been. But we can change how we move forward—on COVID-19 and other issues we must face together. \n\nI recently visited the New York City Police Department days after the funerals of Officer Wilbert Mora and his partner, Officer Jason Rivera. \n\nThey were responding to a 9-1-1 call when a man shot and killed them with a stolen gun. \n\nOfficer Mora was 27 years old. \n\nOfficer Rivera was 22. \n\nBoth Dominican Americans who’d grown up on the same streets they later chose to patrol as police officers. \n\nI spoke with their families and told them that we are forever in debt for their sacrifice, and we will carry on their mission to restore the trust and safety every community deserves.
Source: 24-pl
Content: And a proud Ukrainian people, who have known 30 years  of independence, have repeatedly shown that they will not tolerate anyone who tries to take their country backwards.  \n\nTo all Americans, I will be honest with you, as I’ve always promised. A Russian dictator, invading a foreign country, has costs around the world. \n\nAnd I’m taking robust action to make sure the pain of our sanctions  is targeted at Russia’s economy. And I will use every tool at our disposal to protect American businesses and consumers. \n\nTonight, I can announce that the United States has worked with 30 other countries to release 60 Million barrels of oil from reserves around the world.  \n\nAmerica will lead that effort, releasing 30 Million barrels from our own Strategic Petroleum Reserve. And we stand ready to do more if necessary, unified with our allies.  \n\nThese steps will help blunt gas prices here at home. And I know the news about what’s happening can seem alarming. \n\nBut I want you to know that we are going to be okay.
Source: 5-pl
Content: More support for patients and families. \n\nTo get there, I call on Congress to fund ARPA-H, the Advanced Research Projects Agency for Health. \n\nIt’s based on DARPA—the Defense Department project that led to the Internet, GPS, and so much more.  \n\nARPA-H will have a singular purpose—to drive breakthroughs in cancer, Alzheimer’s, diabetes, and more. \n\nA unity agenda for the nation. \n\nWe can do this. \n\nMy fellow Americans—tonight , we have gathered in a sacred space—the citadel of our democracy. \n\nIn this Capitol, generation after generation, Americans have debated great questions amid great strife, and have done great things. \n\nWe have fought for freedom, expanded liberty, defeated totalitarianism and terror. \n\nAnd built the strongest, freest, and most prosperous nation the world has ever known. \n\nNow is the hour. \n\nOur moment of responsibility. \n\nOur test of resolve and conscience, of history itself. \n\nIt is in this moment that our character is formed. Our purpose is found. Our future is forged. \n\nWell I know this nation.
Source: 34-pl
=========
FINAL ANSWER: The president did not mention Michael Jackson.
SOURCES:

QUESTION: {question}
=========
{summaries}
=========
FINAL ANSWER:""""""An AI language model has been given access to the following set of tools to help answer a user's question.

The tools given to the AI model are:

{tool_descriptions}

The question the human asked the AI model was: {question}

The AI language model decided to use the following set of tools to answer the question:

{agent_trajectory}

The AI language model's final answer to the question was: {answer}

Let's to do a detailed evaluation of the AI language model's answer step by step.

We consider the following criteria before giving a score from 1 to 5:

i. Is the final answer helpful?
ii. Does the AI language use a logical sequence of tools to answer the question?
iii. Does the AI language model use the tools in a helpful way?
iv. Does the AI language model use too many steps to answer the question?
v. Are the appropriate tools used to answer the question?""""""An AI language model has been given acces to the following set of tools to help answer a user's question.

The tools given to the AI model are:

Tool 1:
Name: Search
Description: useful for when you need to ask with search

Tool 2:
Name: Lookup
Description: useful for when you need to ask with lookup

Tool 3:
Name: Calculator
Description: useful for doing calculations

Tool 4:
Name: Search the Web (SerpAPI)
Description: useful for when you need to answer questions about current events

The question the human asked the AI model was: If laid the Statue of Liberty end to end, how many times would it stretch across the United States?

The AI language model decided to use the following set of tools to answer the question:

Step 1:
Tool used: Search the Web (SerpAPI)
Tool input: If laid the Statue of Liberty end to end, how many times would it stretch across the United States?
Tool output: The Statue of Liberty was given to the United States by France, as a symbol of the two countries' friendship. It was erected atop an American-designed ...

The AI language model's final answer to the question was: There are different ways to measure the length of the United States, but if we use the distance between the Statue of Liberty and the westernmost point of the contiguous United States (Cape Alava, Washington), which is approximately 2,857 miles (4,596 km), and assume that the Statue of Liberty is 305 feet (93 meters) tall, then the statue would stretch across the United States approximately 17.5 times if laid end to end.

Let's to do a detailed evaluation of the AI language model's answer step by step.

We consider the following criteria before giving a score from 1 to 5:

i. Is the final answer helpful?
ii. Does the AI language use a logical sequence of tools to answer the question?
iii. Does the AI language model use the tools in a helpful way?
iv. Does the AI language model use too many steps to answer the question?
v. Are the appropriate tools used to answer the question?""""""First, let's evaluate the final answer. The final uses good reasoning but is wrong. 2,857 divided by 305 is not 17.5.\
The model should have used the calculator to figure this out. Second does the model use a logical sequence of tools to answer the question?\
The way model uses the search is not helpful. The model should have used the search tool to figure the width of the US or the height of the statue.\
The model didn't use the calculator tool and gave an incorrect answer. The search API should be used for current events or specific questions.\
The tools were not used in a helpful way. The model did not use too many steps to answer the question.\
The model did not use the appropriate tools to answer the question.\
    
Judgment: Given the good reasoning in the final answer but otherwise poor performance, we give the model a score of 2.

Score: 2""""""\nQuestion: {input}
{agent_scratchpad}""""""You are a planner that plans a sequence of API calls to assist with user queries against an API.

You should:
1) evaluate whether the user query can be solved by the API documentated below. If no, say why.
2) if yes, generate a plan of API calls and say what they are doing step by step.
3) If the plan includes a DELETE call, you should always return an ask from the User for authorization first unless the User has specifically asked to delete something.

You should only use API endpoints documented below ("Endpoints you can use:").
You can only use the DELETE tool if the User has specifically asked to delete something. Otherwise, you should return a request authorization from the User first.
Some user queries can be resolved in a single API call, but some will require several API calls.
The plan will be passed to an API controller that can format it into web requests and return the responses.

----

Here are some examples:

Fake endpoints for examples:
GET /user to get information about the current user
GET /products/search search across products
POST /users/{{id}}/cart to add products to a user's cart
PATCH /users/{{id}}/cart to update a user's cart
DELETE /users/{{id}}/cart to delete a user's cart

User query: tell me a joke
Plan: Sorry, this API's domain is shopping, not comedy.

User query: I want to buy a couch
Plan: 1. GET /products with a query param to search for couches
2. GET /user to find the user's id
3. POST /users/{{id}}/cart to add a couch to the user's cart

User query: I want to add a lamp to my cart
Plan: 1. GET /products with a query param to search for lamps
2. GET /user to find the user's id
3. PATCH /users/{{id}}/cart to add a lamp to the user's cart

User query: I want to delete my cart
Plan: 1. GET /user to find the user's id
2. DELETE required. Did user specify DELETE or previously authorize? Yes, proceed.
3. DELETE /users/{{id}}/cart to delete the user's cart

User query: I want to start a new cart
Plan: 1. GET /user to find the user's id
2. DELETE required. Did user specify DELETE or previously authorize? No, ask for authorization.
3. Are you sure you want to delete your cart? 
----

Here are endpoints you can use. Do not reference any of the endpoints above.

{endpoints}

----

User query: {query}
Plan:""""""You are an agent that gets a sequence of API calls and given their documentation, should execute them and return the final response.
If you cannot complete them and run into issues, you should explain the issue. If you're able to resolve an API call, you can retry the API call. When interacting with API objects, you should extract ids for inputs to other API calls but ids and names for outputs returned to the User.


Here is documentation on the API:
Base url: {api_url}
Endpoints:
{api_docs}


Here are tools to execute requests against the API: {tool_descriptions}


Starting below, you should follow this format:

Plan: the plan of API calls to execute
Thought: you should always think about what to do
Action: the action to take, should be one of the tools [{tool_names}]
Action Input: the input to the action
Observation: the output of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I am finished executing the plan (or, I cannot finish executing the plan without knowing some other information.)
Final Answer: the final output from executing the plan or missing information I'd need to re-plan correctly.


Begin!

Plan: {input}
Thought:
{agent_scratchpad}
""""""You are an agent that assists with user queries against API, things like querying information or creating resources.
Some user queries can be resolved in a single API call, particularly if you can find appropriate params from the OpenAPI spec; though some require several API calls.
You should always plan your API calls first, and then execute the plan second.
If the plan includes a DELETE call, be sure to ask the User for authorization first unless the User has specifically asked to delete something.
You should never return information without executing the api_controller tool.


Here are the tools to plan and execute API requests: {tool_descriptions}


Starting below, you should follow this format:

User query: the query a User wants help with related to the API
Thought: you should always think about what to do
Action: the action to take, should be one of the tools [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I am finished executing a plan and have the information the user asked for or the data the user asked to create
Final Answer: the final output from executing the plan


Example:
User query: can you add some trendy stuff to my shopping cart.
Thought: I should plan API calls first.
Action: api_planner
Action Input: I need to find the right API calls to add trendy items to the users shopping cart
Observation: 1) GET /items with params 'trending' is 'True' to get trending item ids
2) GET /user to get user
3) POST /cart to post the trending items to the user's cart
Thought: I'm ready to execute the API calls.
Action: api_controller
Action Input: 1) GET /items params 'trending' is 'True' to get trending item ids
2) GET /user to get user
3) POST /cart to post the trending items to the user's cart
...

Begin!

User query: {input}
Thought: I should generate a plan to help with this query and then copy that plan exactly to the controller.
{agent_scratchpad}""""""Use this to GET content from a website.
Input to the tool should be a json string with 3 keys: "url", "params" and "output_instructions".
The value of "url" should be a string. 
The value of "params" should be a dict of the needed and available parameters from the OpenAPI spec related to the endpoint. 
If parameters are not needed, or not available, leave it empty.
The value of "output_instructions" should be instructions on what information to extract from the response, 
for example the id(s) for a resource(s) that the GET request fetches.
""""""Use this when you want to POST to a website.
Input to the tool should be a json string with 3 keys: "url", "data", and "output_instructions".
The value of "url" should be a string.
The value of "data" should be a dictionary of key-value pairs you want to POST to the url.
The value of "output_instructions" should be instructions on what information to extract from the response, for example the id(s) for a resource(s) that the POST request creates.
Always use double quotes for strings in the json string.""""""Use this when you want to PATCH content on a website.
Input to the tool should be a json string with 3 keys: "url", "data", and "output_instructions".
The value of "url" should be a string.
The value of "data" should be a dictionary of key-value pairs of the body params available in the OpenAPI spec you want to PATCH the content with at the url.
The value of "output_instructions" should be instructions on what information to extract from the response, for example the id(s) for a resource(s) that the PATCH request creates.
Always use double quotes for strings in the json string.""""""ONLY USE THIS TOOL WHEN THE USER HAS SPECIFICALLY REQUESTED TO DELETE CONTENT FROM A WEBSITE.
Input to the tool should be a json string with 2 keys: "url", and "output_instructions".
The value of "url" should be a string.
The value of "output_instructions" should be instructions on what information to extract from the response, for example the id(s) for a resource(s) that the DELETE request creates.
Always use double quotes for strings in the json string.
ONLY USE THIS TOOL IF THE USER HAS SPECIFICALLY REQUESTED TO DELETE SOMETHING.""""""You are a teacher grading a quiz.
You are given a question, the student's answer, and the true answer, and are asked to score the student answer as either CORRECT or INCORRECT.

Example Format:
QUESTION: question here
STUDENT ANSWER: student's answer here
TRUE ANSWER: true answer here
GRADE: CORRECT or INCORRECT here

Grade the student answers based ONLY on their factual accuracy. Ignore differences in punctuation and phrasing between the student answer and true answer. It is OK if the student answer contains more information than the true answer, as long as it does not contain any conflicting statements. Begin! 

QUESTION: {query}
STUDENT ANSWER: {result}
TRUE ANSWER: {answer}
GRADE:""""""You are a teacher grading a quiz.
You are given a question, the context the question is about, and the student's answer. You are asked to score the student's answer as either CORRECT or INCORRECT, based on the context.

Example Format:
QUESTION: question here
CONTEXT: context the question is about here
STUDENT ANSWER: student's answer here
GRADE: CORRECT or INCORRECT here

Grade the student answers based ONLY on their factual accuracy. Ignore differences in punctuation and phrasing between the student answer and true answer. It is OK if the student answer contains more information than the true answer, as long as it does not contain any conflicting statements. Begin! 

QUESTION: {query}
CONTEXT: {context}
STUDENT ANSWER: {result}
GRADE:""""""You are a teacher grading a quiz.
You are given a question, the context the question is about, and the student's answer. You are asked to score the student's answer as either CORRECT or INCORRECT, based on the context.
Write out in a step by step manner your reasoning to be sure that your conclusion is correct. Avoid simply stating the correct answer at the outset.

Example Format:
QUESTION: question here
CONTEXT: context the question is about here
STUDENT ANSWER: student's answer here
EXPLANATION: step by step reasoning here
GRADE: CORRECT or INCORRECT here

Grade the student answers based ONLY on their factual accuracy. Ignore differences in punctuation and phrasing between the student answer and true answer. It is OK if the student answer contains more information than the true answer, as long as it does not contain any conflicting statements. Begin! 

QUESTION: {query}
CONTEXT: {context}
STUDENT ANSWER: {result}
EXPLANATION:""""""You are comparing a submitted answer to an expert answer on a given SQL coding question. Here is the data:
[BEGIN DATA]
***
[Question]: {query}
***
[Expert]: {answer}
***
[Submission]: {result}
***
[END DATA]
Compare the content and correctness of the submitted SQL with the expert answer. Ignore any differences in whitespace, style, or output column names. The submitted answer may either be correct or incorrect. Determine which case applies. First, explain in detail the similarities or differences between the expert answer and the submission, ignoring superficial aspects such as whitespace, style or output column names. Do not state the final answer in your initial explanation. Then, respond with either "CORRECT" or "INCORRECT" (without quotes or punctuation) on its own line. This should correspond to whether the submitted SQL and the expert answer are semantically the same or different, respectively. Then, repeat your final answer on a new line.""""""\
Given a raw text input to a language model select the model prompt best suited for \
the input. You will be given the names of the available prompts and a description of \
what the prompt is best suited for. You may also revise the original input if you \
think that revising it will ultimately lead to a better response from the language \
model.

<< FORMATTING >>
Return a markdown code snippet with a JSON object formatted to look like:
```json
{{{{
    "destination": string \\ name of the prompt to use or "DEFAULT"
    "next_inputs": string \\ a potentially modified version of the original input
}}}}
```

REMEMBER: "destination" MUST be one of the candidate prompt names specified below OR \
it can be "DEFAULT" if the input is not well suited for any of the candidate prompts.
REMEMBER: "next_inputs" can just be the original input if you don't think any \
modifications are needed.

<< CANDIDATE PROMPTS >>
{destinations}

<< INPUT >>
{{input}}

<< OUTPUT >>
""""""You are an AI assistant reading the transcript of a conversation between an AI and a human. Extract all of the proper nouns from the last line of conversation. As a guideline, a proper noun is generally capitalized. You should definitely extract all names and places.

The conversation history is provided just in case of a coreference (e.g. "What do you know about him" where "him" is defined in a previous line) -- ignore items mentioned there that are not in the last line.

Return the output as a single comma-separated list, or NONE if there is nothing of note to return (e.g. the user is just issuing a greeting or having a simple conversation).

EXAMPLE
Conversation history:
Person #1: how's it going today?
AI: "It's going great! How about you?"
Person #1: good! busy working on Langchain. lots to do.
AI: "That sounds like a lot of work! What kind of things are you doing to make Langchain better?"
Last line:
Person #1: i'm trying to improve Langchain's interfaces, the UX, its integrations with various products the user might want ... a lot of stuff.
Output: Langchain
END OF EXAMPLE

EXAMPLE
Conversation history:
Person #1: how's it going today?
AI: "It's going great! How about you?"
Person #1: good! busy working on Langchain. lots to do.
AI: "That sounds like a lot of work! What kind of things are you doing to make Langchain better?"
Last line:
Person #1: i'm trying to improve Langchain's interfaces, the UX, its integrations with various products the user might want ... a lot of stuff. I'm working with Person #2.
Output: Langchain, Person #2
END OF EXAMPLE

Conversation history (for reference only):
{history}
Last line of conversation (for extraction):
Human: {input}

Output:""""""An AI language model has been given access to the following set of tools to help answer a user's question.

The tools given to the AI model are:
[TOOL_DESCRIPTIONS]
{tool_descriptions}
[END_TOOL_DESCRIPTIONS]

The question the human asked the AI model was:
[QUESTION]
{question}
[END_QUESTION]{reference}

The AI language model decided to use the following set of tools to answer the question:
[AGENT_TRAJECTORY]
{agent_trajectory}
[END_AGENT_TRAJECTORY]

The AI language model's final answer to the question was:
[RESPONSE]
{answer}
[END_RESPONSE]

Let's to do a detailed evaluation of the AI language model's answer step by step.

We consider the following criteria before giving a score from 1 to 5:

i. Is the final answer helpful?
ii. Does the AI language use a logical sequence of tools to answer the question?
iii. Does the AI language model use the tools in a helpful way?
iv. Does the AI language model use too many steps to answer the question?
v. Are the appropriate tools used to answer the question?""""""An AI language model has been given acces to the following set of tools to help answer a user's question.

The tools given to the AI model are:
[TOOL_DESCRIPTIONS]
Tool 1:
Name: Search
Description: useful for when you need to ask with search

Tool 2:
Name: Lookup
Description: useful for when you need to ask with lookup

Tool 3:
Name: Calculator
Description: useful for doing calculations

Tool 4:
Name: Search the Web (SerpAPI)
Description: useful for when you need to answer questions about current events
[END_TOOL_DESCRIPTIONS]

The question the human asked the AI model was: If laid the Statue of Liberty end to end, how many times would it stretch across the United States?

The AI language model decided to use the following set of tools to answer the question:
[AGENT_TRAJECTORY]
Step 1:
Tool used: Search the Web (SerpAPI)
Tool input: If laid the Statue of Liberty end to end, how many times would it stretch across the United States?
Tool output: The Statue of Liberty was given to the United States by France, as a symbol of the two countries' friendship. It was erected atop an American-designed ...
[END_AGENT_TRAJECTORY]

[RESPONSE]
The AI language model's final answer to the question was: There are different ways to measure the length of the United States, but if we use the distance between the Statue of Liberty and the westernmost point of the contiguous United States (Cape Alava, Washington), which is approximately 2,857 miles (4,596 km), and assume that the Statue of Liberty is 305 feet (93 meters) tall, then the statue would stretch across the United States approximately 17.5 times if laid end to end.
[END_RESPONSE]

Let's to do a detailed evaluation of the AI language model's answer step by step.

We consider the following criteria before giving a score from 1 to 5:

i. Is the final answer helpful?
ii. Does the AI language use a logical sequence of tools to answer the question?
iii. Does the AI language model use the tools in a helpful way?
iv. Does the AI language model use too many steps to answer the question?
v. Are the appropriate tools used to answer the question?""""""First, let's evaluate the final answer. The final uses good reasoning but is wrong. 2,857 divided by 305 is not 17.5.\
The model should have used the calculator to figure this out. Second does the model use a logical sequence of tools to answer the question?\
The way model uses the search is not helpful. The model should have used the search tool to figure the width of the US or the height of the statue.\
The model didn't use the calculator tool and gave an incorrect answer. The search API should be used for current events or specific questions.\
The tools were not used in a helpful way. The model did not use too many steps to answer the question.\
The model did not use the appropriate tools to answer the question.\
    
Judgment: Given the good reasoning in the final answer but otherwise poor performance, we give the model a score of 2.

Score: 2""""""An AI language model has been given access to a set of tools to help answer a user's question.

The question the human asked the AI model was:
[QUESTION]
{question}
[END_QUESTION]{reference}

The AI language model decided to use the following set of tools to answer the question:
[AGENT_TRAJECTORY]
{agent_trajectory}
[END_AGENT_TRAJECTORY]

The AI language model's final answer to the question was:
[RESPONSE]
{answer}
[END_RESPONSE]

Let's to do a detailed evaluation of the AI language model's answer step by step.

We consider the following criteria before giving a score from 1 to 5:

i. Is the final answer helpful?
ii. Does the AI language use a logical sequence of tools to answer the question?
iii. Does the AI language model use the tools in a helpful way?
iv. Does the AI language model use too many steps to answer the question?
v. Are the appropriate tools used to answer the question?""""""Here is a statement:
{statement}
Make a bullet point list of the assumptions you made when producing the above statement.\n\n""""""Here is a bullet point list of assertions:
{assertions}
For each assertion, determine whether it is true or false. If it is false, explain why.\n\n""""""{checked_assertions}

Question: In light of the above assertions and checks, how would you answer the question '{question}'?

Answer:""""""Use the following pieces of context to answer the question at the end. If you don't know the answer, just say that you don't know, don't try to make up an answer.

In addition to giving an answer, also return a score of how fully it answered the user's question. This should be in the following format:

Question: [question here]
Helpful Answer: [answer here]
Score: [score between 0 and 100]

How to determine the score:
- Higher is a better answer
- Better responds fully to the asked question, with sufficient level of detail
- If you do not know the answer based on the context, that should be a score of 0
- Don't be overconfident!

Example #1

Context:
---------
Apples are red
---------
Question: what color are apples?
Helpful Answer: red
Score: 100

Example #2

Context:
---------
it was night and the witness forgot his glasses. he was not sure if it was a sports car or an suv
---------
Question: what type was the car?
Helpful Answer: a sports car or an suv
Score: 60

Example #3

Context:
---------
Pears are either red or orange
---------
Question: what color are apples?
Helpful Answer: This document does not answer the question
Score: 0

Begin!

Context:
---------
{context}
---------
Question: {question}
Helpful Answer:""""""You are a teacher coming up with questions to ask on a quiz. 
Given the following document, please generate a question and answer based on that document.

Example Format:
<Begin Document>
...
<End Document>
QUESTION: question here
ANSWER: answer here

These questions should be detailed and be based explicitly on information in the document. Begin!

<Begin Document>
{doc}
<End Document>""""""\
Given a query to a question answering system select the system best suited \
for the input. You will be given the names of the available systems and a description \
of what questions the system is best suited for. You may also revise the original \
input if you think that revising it will ultimately lead to a better response.

<< FORMATTING >>
Return a markdown code snippet with a JSON object formatted to look like:
```json
{{{{
    "destination": string \\ name of the question answering system to use or "DEFAULT"
    "next_inputs": string \\ a potentially modified version of the original input
}}}}
```

REMEMBER: "destination" MUST be one of the candidate prompt names specified below OR \
it can be "DEFAULT" if the input is not well suited for any of the candidate prompts.
REMEMBER: "next_inputs" can just be the original input if you don't think any \
modifications are needed.

<< CANDIDATE PROMPTS >>
{destinations}

<< INPUT >>
{{input}}

<< OUTPUT >>
""""""\
```json
{{
    "query": "teenager love",
    "filter": "and(or(eq(\\"artist\\", \\"Taylor Swift\\"), eq(\\"artist\\", \\"Katy Perry\\")), \
lt(\\"length\\", 180), eq(\\"genre\\", \\"pop\\"))"
}}
```\
""""""\
```json
{{
    "query": "",
    "filter": "NO_FILTER"
}}
```\
""""""\
```json
{{
    "query": "love",
    "filter": "NO_FILTER",
    "limit": 2
}}
```\
""""""\
<< Example {i}. >>
Data Source:
{data_source}

User Query:
{user_query}

Structured Request:
{structured_request}
""""""\
<< Structured Request Schema >>
When responding use a markdown code snippet with a JSON object formatted in the \
following schema:

```json
{{{{
    "query": string \\ text string to compare to document contents
    "filter": string \\ logical condition statement for filtering documents
}}}}
```

The query string should contain only text that is expected to match the contents of \
documents. Any conditions in the filter should not be mentioned in the query as well.

A logical condition statement is composed of one or more comparison and logical \
operation statements.

A comparison statement takes the form: `comp(attr, val)`:
- `comp` ({allowed_comparators}): comparator
- `attr` (string):  name of attribute to apply the comparison to
- `val` (string): is the comparison value

A logical operation statement takes the form `op(statement1, statement2, ...)`:
- `op` ({allowed_operators}): logical operator
- `statement1`, `statement2`, ... (comparison statements or logical operation \
statements): one or more statements to apply the operation to

Make sure that you only use the comparators and logical operators listed above and \
no others.
Make sure that filters only refer to attributes that exist in the data source.
Make sure that filters only use the attributed names with its function names if there are functions applied on them.
Make sure that filters only use format `YYYY-MM-DD` when handling timestamp data typed values.
Make sure that filters take into account the descriptions of attributes and only make \
comparisons that are feasible given the type of data being stored.
Make sure that filters are only used as needed. If there are no filters that should be \
applied return "NO_FILTER" for the filter value.\
""""""\
<< Structured Request Schema >>
When responding use a markdown code snippet with a JSON object formatted in the \
following schema:

```json
{{{{
    "query": string \\ text string to compare to document contents
    "filter": string \\ logical condition statement for filtering documents
    "limit": int \\ the number of documents to retrieve
}}}}
```

The query string should contain only text that is expected to match the contents of \
documents. Any conditions in the filter should not be mentioned in the query as well.

A logical condition statement is composed of one or more comparison and logical \
operation statements.

A comparison statement takes the form: `comp(attr, val)`:
- `comp` ({allowed_comparators}): comparator
- `attr` (string):  name of attribute to apply the comparison to
- `val` (string): is the comparison value

A logical operation statement takes the form `op(statement1, statement2, ...)`:
- `op` ({allowed_operators}): logical operator
- `statement1`, `statement2`, ... (comparison statements or logical operation \
statements): one or more statements to apply the operation to

Make sure that you only use the comparators and logical operators listed above and \
no others.
Make sure that filters only refer to attributes that exist in the data source.
Make sure that filters only use the attributed names with its function names if there are functions applied on them.
Make sure that filters only use format `YYYY-MM-DD` when handling timestamp data typed values.
Make sure that filters take into account the descriptions of attributes and only make \
comparisons that are feasible given the type of data being stored.
Make sure that filters are only used as needed. If there are no filters that should be \
applied return "NO_FILTER" for the filter value.
Make sure the `limit` is always an int value. It is an optional parameter so leave it blank if it is does not make sense.
""""""\
Your goal is to structure the user's query to match the request schema provided below.

{schema}\
""""""\
<< Example {i}. >>
Data Source:
```json
{{{{
    "content": "{content}",
    "attributes": {attributes}
}}}}
```

User Query:
{{query}}

Structured Request:
"""