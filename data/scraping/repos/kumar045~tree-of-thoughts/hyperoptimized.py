import concurrent.futures
from abc import ABC, abstractmethod
import openai

class AbstractLanguageModel(ABC):
    @abstractmethod
    def generate_thoughts(self, state, k):
        pass

    @abstractmethod
    def evaluate_states(self, states):
        pass


class CustomLanguageModel(AbstractLanguageModel):
    def __init__(self, model):
        self.model = model

    def generate_thoughts(self, state, k):
        #implement the thought generation logic using self.model
        pass

    def evaluate_states(self, states):
        #implement state evaluation logic using self.model
        pass
class OpenAILanguageModel(AbstractLanguageModel):
    def __init__(self, api_key, strategy="cot", evaluation_strategy="value"):
        openai.api_key = api_key
        self.strategy = strategy
        self.evaluation_strategy = evaluation_strategy

    def generate_thoughts(self, state, k):
        state_text = ' '.join(state)
        
        prompt = f"Given the current state of reasoning: '{state_text}', generate {k} coherent thoughts to continue the reasoning process:"
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            n=k,
            max_tokens=50,
            stop=None,
            temperature=0.5,
        )
        thoughts = [choice.text.strip() for choice in response.choices]
        print(thoughts)
        return thoughts

    def evaluate_states(self, states):
        if self.evaluation_strategy == 'value':
            state_values = {}
            for state in states:
                state_text = ' '.join(state)
                prompt = f"Given the current state of reasoning: '{state_text}', evaluate its value as a float between 0 and 1:"
                response = openai.Completion.create(
                    engine="text-davinci-003",
                    prompt=prompt,
                    n=1,
                    max_tokens=10,
                    stop=None,
                    temperature=0.5,
                )
                try:
                    # print(response.choices[0].text.strip())
                    value = float(response.choices[0].text.strip())
                    print(value)
                except ValueError:
                    value = 0  # Assign a default value if the conversion fails
                state_values[state] = value
            return state_values

        elif self.evaluation_strategy == 'vote':
            states_text = '\n'.join([' '.join(state) for state in states])
            prompt = f"Given the following states of reasoning, vote for the best state:\n{states_text}\n\nVote:"
            response = openai.Completion.create(
                engine="text-davinci-003",
                prompt=prompt,
                n=1,
                max_tokens=50,
                stop=None,
                temperature=0.5,
            )
            best_state_text = response.choices[0].text.strip()
            print(best_state_text)
            best_state = tuple(best_state_text.split())
            return {state: 1 if state == best_state else 0 for state in states}

        else:
            raise ValueError("Invalid evaluation strategy. Choose 'value' or 'vote'.")

class OptimizedOpenAILanguageModel(OpenAILanguageModel):
    def __init__(self, api_key, strategy="cot", evaluation_strategy="value", cache_enabled=True):
        super().__init__(api_key, strategy, evaluation_strategy)
        self.cache_enabled = cache_enabled
        self.thought_cache = {}
        self.state_evaluation_cache = {}

    def parallel_generate_thoughts(self, states, k):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            thoughts = list(executor.map(lambda state: self.generate_thoughts(state, k), states))
            print(thoughts)
        return thoughts

    def parallel_evaluate_states(self, states):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            state_values = list(executor.map(self.evaluate_states, states))
            print(state_values)
        return state_values
    

# model = OptimizedOpenAILanguageModel('your_openai_api_key_here')

#update tree of thoughts to use optimized models mehtods

class TreeofThoughts:
    """
    1. Thought Decomposition --> based on problem properties

    2. Thought Generator -> create a thought generator function G(p0, s, k) with 2 strategies a sample iid thoughts from a cot prompt b. propose thoughts
    sequentially using a propose prompt

    3. create a state evaluator function V(p0, S) with 2 strategies a value each state independently b. vote across states

    4. Choose a search algo based on tree structure [BFS or DFS]

    Implement chosen search algorithm for bfs (algo1):
        init S0 with the input x
        for t = 1 to T (step limit):
            generate candidate thoughts for each state in St-1
            eveluate the candiate states using the state evaluator V
            select the b most promising states for St

        return the final output by genertaing the thought for the best state in St for DFS(algo2)

        defien a recurseive DFS function with the current state s, step t, and other required params

        if t > T record the output by generating the thought for current state S

        for each candidate state s in the sorted list of generated thoughts for s:
            
            if the evaluated value of s is greater the the threshold of vth call the dfs function recursively
            with s and t + 1

    execute the chosen search algo with the input problem, thought generator, and state evaluator, and other required params
    """

    def __init__(self, model, search_algorithm):
        self.model = model
        self.search_algorithm = search_algorithm

    def solve(self, x, k, T, b, vth):
        if self.search_algorithm == 'BFS':
            return self.tot_bfs(x, k, T, b)
        elif self.search_algorithm == 'DFS':
            return self.tot_dfs(x, k, T, vth)
        else:
            raise ValueError("Invalid search algorithm. Choose 'BFS' or 'DFS'.")

    def tot_bfs(self, x, k, T, b):
        S0 = {x}
        for t in range(1, T + 1):
            S0_t = {(*s, z) for s in S0 for z in self.model.generate_thoughts(s, k)}
            Vt = self.model.evaluate_states(S0_t)
            St = sorted(S0_t, key=lambda s: Vt[s], reverse=True)[:b]
            S0 = set(St)
        return self.model.generate_thoughts(max(St, key=lambda s: Vt[s]), 1)

    def tot_dfs(self, x, k, T, vth):
        output = []

        def dfs(s, t):
            if t > T:
                output.append(self.model.generate_thoughts(s, 1))
                return
            for s_prime in sorted(self.model.generate_thoughts(s, k)):
                if self.model.evaluate_states({s_prime})[s_prime] > vth:
                    dfs((*s, s_prime), t + 1)

        dfs(x, 1)
        return output


#does not output state after each thought --- idk why -- needs work
class OptimizedTreeofThoughts(TreeofThoughts):
    def tot_bfs(self, x, k, T, b):
        S0 = {x}
        for t in range(1, T + 1):
            S0_t = {(*s, z) for s in S0 for z in self.model.parallel_generate_thoughts(s, k)}
            Vt = self.model.parallel_evaluate_states(S0_t)
            St = sorted(S0_t, key=lambda s: Vt[s], reverse=True)[:b]
            S0 = set(St)
        return self.model.generate_thoughts(max(St, key=lambda s: Vt[s]), 1)

    def tot_dfs(self, x, k, T, vth):
        output = []

        def dfs(s, t):
            if t > T:
                output.append(self.model.generate_thoughts(s, 1))
                return
            for s_prime in sorted(self.model.generate_thoughts(s, k)):
                if self.model.evaluate_states({s_prime})[s_prime] > vth:
                    dfs((*s, s_prime), t + 1)

        dfs(x, 1)
        return output

    


search_algorithm = "DFS"
strategy = "cot"
evaluation_strategy="value"

#create instance
model = OptimizedOpenAILanguageModel('')

tree_of_thoughts = OptimizedTreeofThoughts(model, search_algorithm)

input_problem = "What are the best reasoning methods to advance Large Language Models"
k = 5
T = 3
b = 5
vth = 0.5


#call the solve emthod with the input problem and other params
solution = tree_of_thoughts.solve(input_problem, k, T, b, vth)

#use the solution in env
print(solution)