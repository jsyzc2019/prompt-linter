# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/03_api.ipynb.

# %% auto 0
__all__ = ['BaseAPI', 'CalculatorAPI', 'WolframeAPI']

# %% ../nbs/03_api.ipynb 4
from abc import abstractclassmethod

import wolframalpha
from langchain import PromptTemplate

# %% ../nbs/03_api.ipynb 6
class BaseAPI:
    def __init__(
        self,
        name: str, # the name of the API call
        prompt_template: PromptTemplate,
        sampling_threshold: float = 0.2,
        filtering_threshold: float = 0.2,
    ):
        self.name = name
        self.prompt_template = prompt_template
        self.sampling_threshold = sampling_threshold
        self.filtering_threshold = filtering_threshold

    @abstractclassmethod
    def execute(self):
        pass
    
    def __call__(self, *args: str, **kargs: str) -> str:
        output = self.execute(*args, **kargs)
        return str(output)

# %% ../nbs/03_api.ipynb 8
class CalculatorAPI(BaseAPI):
    def execute(self, input: str) -> str:
        try:
            return eval(input)
        except:
            return ""

# %% ../nbs/03_api.ipynb 10
class WolframeAPI(BaseAPI):
    def __init__(self, *args, api_key: str, **kargs):
        super().__init__(*args, **kargs)
        self.api_key = api_key
        
    def execute(self, input: str) -> str:
        client = wolframalpha.Client(self.api_key)
        res = client.query(input=input)
        return next(res.results).text
