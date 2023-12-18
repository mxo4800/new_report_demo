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


def create_rewrite_report(text):

    template = f"""Hello ChatGPT, today I have a challenging and important task for you. We have an existing report, but we need it to be rewritten to match the style of a report that was created two weeks ago by an analyst. The goal is to maintain the content and data of the current report but adapt it to the stylistic nuances of the previous one.

    First, please review the older report to understand its writing style. Pay close attention to the structure, tone, and the specific way information is presented in it.

    Previous Report Style Reference:
    {text}

    Now, here is the report that needs to be rewritten:

    Current Report:
    
    {{report}}

    Your task is to rework this current report, ensuring that its content and data remain intact, but its style closely resembles that of the previous report. This includes matching the level of detail, tone, and the overall approach to presenting information. 

    We value your assistance in maintaining a consistent and professional style in our reporting, adapting new information to established presentation standards."""

    prompt_template = PromptTemplate(
        input_variables=["report"], template=template)

    return prompt_template


def create_rewrite_chain(text, llm=llm):

    prompt_template = create_rewrite_report(text)

    rewrite_chain = LLMChain(llm=llm, prompt=prompt_template)

    return rewrite_chain


def run_rewrite_chain(text, ai_report, llm=llm):

    rewrite_chain = create_rewrite_chain(text, llm=llm)

    rewritten_report = rewrite_chain.run(ai_report)

    return rewritten_report
