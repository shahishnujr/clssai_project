import os
os.environ['OPENAI_API_KEY'] = 'sk-proj-2xj1ORRwGPwb7VFSUQnjT3BlbkFJxQxUU8A1qVZqglnSnpP3'
from langchain.llms import OpenAI
llm = OpenAI(temperature = 0.6)
n = llm("suggest a name")
print(n)