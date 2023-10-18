import openai
import os
from dotenv import load_dotenv
import time
import cProfile

load_dotenv()
openai.api_key = "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"
model_engine = "gpt-3.5-turbo-0613"


def get_recipes():
    start_time = time.time()
    print("Starting at:", start_time)

    GPT_messages = [
        {"role": "system", "content": "create three recipes with the ingredients: egg, flour, sugar, milk"}
    ]

    before_api_call = time.time()
    print("Before API call:", before_api_call)
    print("Elapsed time before API call:", before_api_call - start_time)

    response = openai.ChatCompletion.create(
        model=model_engine,
        messages=GPT_messages,
        temperature=0.5,
    )

    after_api_call = time.time()
    print("After API call:", after_api_call)
    print("Elapsed time for API call:", after_api_call - before_api_call)

    GPT_response = response['choices'][0]['message']['content']

    end_time = time.time()
    print("Ending at:", end_time)
    print("Total elapsed time:", end_time - start_time)

    return GPT_response


if __name__ == '__main__':
    cProfile.run('get_recipes()')
