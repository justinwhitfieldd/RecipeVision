import openai
import os
from dotenv import load_dotenv
import json

load_dotenv()
openai.api_key = os.getenv('OPEN_AI_API_KEY')
model_engine = "gpt-3.5-turbo-0613"
promptFile = open('prompt.txt', 'r')
prompt = promptFile.read()

GPT_messages = [
    {"role": "system", "content": prompt}
]
GPT_functions = [
    {
        "name": "give_recipes",
        "description": "Give recipes to the user, including ingredients and instructions. To only give one recipe, use NULL for the other values",
        "parameters": {
                "type": "object",
                "properties": {
                    "recipe_one_name": {
                        "type": "string","description": "The name of the recipe",},
                    "recipe_one_ingredients": {
                        "type": "string", "description": "the ingredients of the recipe"},
                    "recipe_one_instructions": {
                        "type": "string", "description": "step by step instructions for the recipe"},
                    "recipe_two_name": {
                        "type": "string","description": "The name of the recipe",},
                    "recipe_two_ingredients": {
                        "type": "string", "description": "the ingredients of the recipe"},
                    "recipe_two_instructions": {
                        "type": "string", "description": "step by step instructions for the recipe"},
                    "recipe_three_name": {
                        "type": "string","description": "The name of the recipe",},
                    "recipe_three_ingredients": {
                        "type": "string", "description": "the ingredients of the recipe"},
                    "recipe_three_instructions": {
                        "type": "string", "description": "step by step instructions for the recipe"},
                    },
                },
    },
]
def give_recipes(recipe_one_name, recipe_one_ingredients, recipe_one_instructions, recipe_two_name, recipe_two_ingredients, recipe_two_instructions, recipe_three_name, recipe_three_ingredients, recipe_three_instructions):
    print(f"Recipe Name: {recipe_one_name}")
    print(f"Ingredients: {recipe_one_ingredients}")
    print(f"Instructions:\n{recipe_one_instructions}")
    print("\n")
    print(f"Recipe Name: {recipe_two_name}")
    print(f"Ingredients: {recipe_two_ingredients}")
    print(f"Instructions:\n{recipe_two_instructions}")
    print("\n")
    print(f"Recipe Name: {recipe_three_name}")
    print(f"Ingredients: {recipe_three_ingredients}")
    print(f"Instructions:\n{recipe_three_instructions}")


def get_recipies(ingredients):
    GPT_messages.append({"role": "user", "content": ingredients})
    print("in get_recipies")

    response = openai.ChatCompletion.create(
        model=model_engine,
        messages=GPT_messages,
        temperature=0.5,
        functions=GPT_functions,
        function_call="auto",  # auto is default, but we'll be explicit
    )

    #GPT_response = response['choices'][0]['message']['content']
    GPT_response = response['choices'][0]['message']

    if 'function_call' in GPT_response:
        available_functions = {
            "give_recipes": give_recipes,
        }
        function_name = GPT_response["function_call"]["name"]
        function_to_call = available_functions[function_name]
        function_args = json.loads(GPT_response["function_call"]["arguments"])
        function_response = function_to_call(
            recipe_one_name=function_args.get("recipe_one_name"),
            recipe_one_ingredients=function_args.get("recipe_one_ingredients"),
            recipe_one_instructions=function_args.get("recipe_one_instructions"),
            recipe_two_name=function_args.get("recipe_two_name"),
            recipe_two_ingredients=function_args.get("recipe_two_ingredients"),
            recipe_two_instructions=function_args.get("recipe_two_instructions"),
            recipe_three_name=function_args.get("recipe_three_name"),
            recipe_three_ingredients=function_args.get("recipe_three_ingredients"),
            recipe_three_instructions=function_args.get("recipe_three_instructions"),
        )
        
    return GPT_response
#Example of calling the function
#get_recipies("bread, milk, sugar, salt, eggs, flour")
