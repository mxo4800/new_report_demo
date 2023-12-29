import openai
from langchain import PromptTemplate
from langchain.llms import OpenAI
from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI
import streamlit as st
import os
from dotenv import load_dotenv

# load_dotenv()

openai.api_key = st.secrets["OPENAI_API_KEY"]
# openai.ap_key = os.environ(["OPENAI_API_KEY"])


llm = ChatOpenAI(model_name='gpt-4', max_tokens=4000, temperature=0)


def create_grammar_template(client_name, industry_type, format="YouTube"):
    grammar_template = f"""
    As an analyst for MiQ, a leading programmatic advertising company, you are tasked with analyzing advertising data for {client_name}, a prominent player in the {industry_type} industry. Your objective is to craft a summary that provides insightful and positive reflections on their {format} advertising campaign. 

    The detailed report below contains comprehensive data about the campaign's performance. Your summary should:

    - Extract and highlight key positive insights, relevant to the {industry_type} industry.
    - Emphasize successful aspects and achievements of the campaign.
    - Include notable statistics that demonstrate effective outcomes.
    - Maintain a positive tone, avoiding mention of any negative aspects.

    Detailed Report:
    {{report}}

    Please provide a concise and insightful summary that aligns with the above guidelines.
    """

    return grammar_template


def create_grammar_prompt(client_name, industry_type, format="YouTube"):
    grammar_template = create_grammar_template(
        client_name, industry_type, format=format)

    template = PromptTemplate(
        input_variables=["report"], template=grammar_template)

    return template


def create_grammar_chain(client_name, industry_type, format="YouTube", llm=llm):
    grammar_prompt_template = create_grammar_prompt(
        client_name, industry_type, format=format)
    grammar_chain = LLMChain(llm=llm, prompt=grammar_prompt_template)

    return grammar_chain


def run_grammar_chain(report, client_name, industry_type, format="YouTube", llm=llm):

    grammar_chain = create_grammar_chain(
        client_name, industry_type, format=format, llm=llm)

    generated_report = grammar_chain.run(report)

    return generated_report


def create_rewrite_report():

    template = """The following insight report describes the sucess of a current programmatic marketing campaign that buys ads on the internet for a client through the depictions of quantative and qualitative data.
    Break down the insight report into actionable bullet points that highlights the sucess of the marketing campaign and tells the client how MiQ utilizes that data to make a buying optimization 
    
    Example: 
    
    Insight report input: The Balvenie's programmatic advertising campaign has achieved impressive results across various metrics. Smartphones were the top-performing device type with over 14 million impressions and a click-through rate (CTR) of 0.20%, followed by tablets and connected TVs.

    A.I Assistant output: - Smartphones is a top-performing device driving a 0.20% CTR. MiQ increased spend allocation to Smartphones to further drive performance

    {report}
    
    
    """

    prompt_template = PromptTemplate(
        input_variables=["report"], template=template)

    return prompt_template


def create_rewrite_chain(llm=llm):

    prompt_template = create_rewrite_report()

    rewrite_chain = LLMChain(llm=llm, prompt=prompt_template)

    return rewrite_chain


def run_rewrite_chain(report, llm=llm):

    rewrite_chain = create_rewrite_chain(llm=llm)

    rewritten_report = rewrite_chain.run(report)

    return rewritten_report
