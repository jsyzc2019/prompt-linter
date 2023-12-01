"""Class to generate JS plots for the Analitiq."""
import io
from typing import Type, TypeVar

import pandas as pd
from langchain import LLMChain, OpenAI, PromptTemplate

# from typing import TypeVar, Type


PLOT_TEMPLATE = """Data has been generated by using the following SQL query:

{sql_query}

That query corresponds to the below natural language request:


Here is some sample data to use for the plot. It is a json object with the following structure:
{data_sample}

There is an existing javascript global variable called '{data_variable_name}' that contains
the data from the query above as a json object.
Create javascript code that uses plotly.js to visualize it in the most sensible way possible.
Plot inside 'plot' div. Return only the javascript code with no other explanations.
Make sure your response only includes javascript code.
Do not add any explanation to your response.
"""

T = TypeVar("T", bound="JSCodePlotGenerator")


class JSCodePlotGenerator(object):
    """Class to generate JS plots for the Analitiq project."""

    def __init__(self: Type[T], sql_query: str, data: pd.DataFrame) -> None:
        """Initialize the plot generator.

        Args:
          plot_type: String, the type of plot to generate.
          plot_data: List of dictionaries, the data to plot.
          plot_config: Dictionary, the configuration for the plot.
        """
        self.sql_query = sql_query
        self.data = self._convert_to_datetime(data)

    def _convert_to_datetime(self: Type[T], df: pd.DataFrame) -> pd.DataFrame:
        """Convert all columns to datetime if possible."""
        for col in df.columns:
            try:
                df[col] = pd.to_datetime(df[col].astype(str))
            except Exception:
                continue
        return df

    def generate_plot(self: Type[T], model_name: str = "gpt-4") -> str:
        """Generate the plot."""
        if self.data.empty:
            # TODO: create template
            return "<p>No data available.</p>"

        data_variable_name = "queried_data"
        llm = OpenAI(temperature=0, model_name=model_name)
        llm_chain = LLMChain(llm=llm, prompt=PromptTemplate.from_template(PLOT_TEMPLATE))

        # extract a sample of data to use for the prediction
        sample_size = min(3, len(self.data.index))
        s = io.StringIO()
        self.data.sample(n=sample_size).to_json(s, orient="table", index=False)
        ai_generated_code = llm_chain.predict(
            sql_query=self.sql_query,
            data_variable_name=data_variable_name,
            data_sample=s.getvalue(),
        )

        # TODO: use langchaing output parser
        ai_generated_code = ai_generated_code.replace("```javascript", "").replace("```", "")

        s = io.StringIO()
        # TODO: orient in table to avoid reshaping
        self.data.to_json(s, orient="table", index=False)

        div_js = '<div id="plot"></div>'
        plotly_js = (
            '<script src="https://cdn.plot.ly/plotly-2.20.0.min.js" charset="utf-8"></script>'
        )

        data_js = f"var {data_variable_name} = {s.getvalue()}\n"
        code_js = f"<script>\n{data_js}\n\n{ai_generated_code}\n</script>"

        # Merge all the JS code
        return "\n".join([div_js, plotly_js, code_js])
