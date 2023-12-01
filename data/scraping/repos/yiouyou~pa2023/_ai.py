class AI:
    from typing import List, Dict

    def __init__(self, model="gpt-4", temperature=0.1):
        import openai
        self.model = model
        self.temperature = temperature

    def start(self, system, user):
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ]
        return self.next(messages)

    def fsystem(self, msg):
        return {"role": "system", "content": msg}

    def fuser(self, msg):
        return {"role": "user", "content": msg}

    def fassistant(self, msg):
        return {"role": "assistant", "content": msg}

    def next(self, messages: List[Dict[str, str]], prompt=None):
        from module.logger import logger
        if prompt:
            messages += [{"role": "user", "content": prompt}]
        logger.debug(f"Creating a new chat completion: {messages}")
        import openai
        response = openai.ChatCompletion.create(
            messages=messages,
            stream=True,
            model=self.model,
            temperature=self.temperature,
        )
        chat = []
        for chunk in response:
            # print(f"\nchunk:{chunk}")
            delta = chunk["choices"][0]["delta"]
            # print(f"\ndelta:{delta}")
            msg = delta.get("content", "")
            # print(f"\nmsg:{msg}")
            print(msg, end="")
            chat.append(msg)
        print()
        messages += [{"role": "assistant", "content": "".join(chat)}]
        logger.debug(f"Chat completion finished: {messages}")
        return messages

def fallback_model(model: str) -> str:
    try:
        import openai
        openai.Model.retrieve(model)
        return model
    except openai.InvalidRequestError:
        print(
            f"Model {model} not available for provided API key. Reverting "
            "to gpt-3.5-turbo. Sign up for the GPT-4 wait list here: "
            "https://openai.com/waitlist/gpt-4-api\n"
        )
        return "gpt-3.5-turbo-0613"
