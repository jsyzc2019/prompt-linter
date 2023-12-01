from dataclasses import dataclass

from fastapi import Depends, HTTPException, status, Request

from modal import Stub, Secret, web_endpoint, Image

stub = Stub()

custom_image = Image.debian_slim().pip_install(
    "pygithub", "pymongo", "cohere", "jinja2"
)

GITHUB_APP_ID = 381420


@stub.function(secret=Secret.from_name("backseat"), image=custom_image)
def draft_pull_request(repo_name: str, pr_number: int):
    import os
    import cohere
    from pymongo import MongoClient
    from github import Github, GithubIntegration

    cohere_client = cohere.Client(os.getenv("COHERE_API_KEY"))
    mongo_client = MongoClient(os.getenv("MONGODB_URI"))

    embeddings_collection = mongo_client["backseat"]["embeddings"]

    app = GithubIntegration(GITHUB_APP_ID, os.getenv("GITHUB_APP_PRIVATE_KEY"))
    print("Got integration")

    owner = repo_name.split("/")[0]
    repo = repo_name.split("/")[1]
    print(f"Owner: {owner}, repo: {repo}")
    installation = app.get_installation(owner, repo)
    installation_token = app.get_access_token(installation.id).token

    print(f"Installation token: {installation_token}")

    github = Github(installation_token)

    # list issues
    gh_repo = github.get_repo(repo_name)
    pr = gh_repo.get_pull(pr_number)
    repo_id = gh_repo.id

    print("Found pull request")

    mongo_client["backseat"]["pull_requests"].update_one(
        {
            "type": "pr",
            "repoId": repo_id,
            "issueNumber": pr_number,
        },
        {"$set": {"status": "generating"}},
    )

    pr_content = f"{pr.title}\n\n{pr.body}"

    for comment in pr.get_comments():
        pr_content += f"\n\n{comment.body}"

    head_sha = pr.head.sha
    files_changed = pr.get_files()

    completed_patch = ""

    for file in files_changed:
        path = file.filename
        patch = file.patch
        completed_patch += patch

    pr_content += f"\nPatch:\n{completed_patch}"

    # get the issue's embeddings
    cohere_response = cohere_client.embed(
        texts=[pr_content],
        model="small",
    )

    embedding = cohere_response.embeddings[0]

    contents = embeddings_collection.aggregate(
        [
            {
                "$search": {
                    "index": "embeddings",
                    "knnBeta": {
                        "vector": embedding,
                        "path": "cohereSmallEmbedding",
                        "k": 11,
                        "filter": {
                            "compound": {
                                "mustNot": {
                                    "equals": {
                                        "value": pr_number,
                                        "path": "issueNumber",
                                    },
                                },
                            }
                        },
                    },
                    "scoreDetails": True,
                },
            },
            {
                "$project": {
                    "score": {
                        "$meta": "searchScoreDetails",
                    },
                    "type": 1,
                    "path": 1,
                    "issueNumber": 1,
                    "issueType": 1,
                    "repoId": 1,
                    "text": 1,
                }
            },
        ]
    )

    print("Got similar content")

    # generate the text for relevant issues
    relevant_content = ""

    for content in contents:
        if content["score"]["value"] < 0.85:
            print("Not using content")
            print(content)
            continue

        relevant_content += "\n" + "-" * 80 + "\n"
        relevant_content += f"{content['type']} "
        if content["type"] == "issue" or content["type"] == "pr":
            relevant_content += f"#{content['issueNumber']}"
        elif content["type"] == "file":
            relevant_content += f"{content['path']}"

        # get the issue text
        relevant_content += f"\n{content['text']}\n\n"
        relevant_content += "\n" + "-" * 80 + "\n"

    import jinja2

    # read the prompt from draft_response_prompt.jinja
    template = jinja2.Template(
        """\
You are an AI assistant responsible for helping users review pull requests in open-source projects.

A user has just opened this pull request:
```\n{{ pr_content }}\n```

Draft a response (and only a response) that will be written as if you were the project administrator.

Your tone should be very gracious and helpful. You should not be sarcastic or rude. You should not be overly formal.

You should not include the instructions in your response. Try to keep the response as short as possible.

Your response should be VERY specific and not include generic statements. If you cannot write a specific response, you should not write a response at all.
"""
    )

    # render the prompt
    prompt = template.render(
        pr_content=pr_content,
        relevant_content=relevant_content,
    )

    print("=" * 80)
    print(prompt)
    print("=" * 80)

    # generate the response
    response = cohere_client.generate(
        prompt=prompt,
        model="command",
        max_tokens=500,
        temperature=0.1,
    )

    first_response = response[0].text

    print("Response:")
    print(first_response)

    # update the issue with the similar issues
    mongo_client["backseat"]["pull_requests"].update_one(
        {
            "repoId": repo_id,
            "issueNumber": pr_number,
        },
        {
            "$set": {
                "draftResponse": first_response,
                "status": "done",
            },
        },
    )
