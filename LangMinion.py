import os, sys
import json
import requests
from openai import AzureOpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider

LangMinion_prompt_revise = "I'll input a sentence or paragraph of English text, and you'll need to check for basic grammatical errors, suggest some changes to make it more consistent with American English usage, and explain your changes. Just give your direct answers, don't say other things or ask me other questions."
LangMinion_prompt_translate = "You are an English translator. When I send you content containing Chinese, you need to translate the entire text into English and provide at least three possible translation results. Just give your direct answers, don't say other things or ask me other questions."
LangMinion_prompt_gen_ielts_speak_test = "Please generate standard answers for IELTS speaking questions on a certain topic for me. I will give you a topic or question. If I enter random, you need to randomly generate an IELTS speaking question. Your output needs to follow the following format: first output my original question or the question you generated based on my topic or the question you randomly generated, then you give a standard answer. The answer needs to meet the requirements of the IELTS speaking test as much as possible, and then explain some highlight sentences or scoring sentences. Finally, give the Chinese translation and Korean translation of this answer.  Just give your direct answers, don't say other things or ask me other questions."
LangMinion_prompt_lookup = "I will provide some English vocabulary. It may be a verb or a noun, or it may be both a verb and a noun, or something else entirely. Please give all its meanings, what their phonetic symbols and pronunciations are, how often it is used first. And then, if this word has a noun form, please tell me whether it is countable, what its singular and plural forms are. If this word has a verb form, please tell me what its first and third person, past tense, past participle, and passive tense are. Please provide three example sentences for each form. Just give your direct answers, don't say other things or ask me other questions."

LangMinion_prompt_dict = {
    'lang_revise' : LangMinion_prompt_revise,
    'lang_trans' : LangMinion_prompt_translate,
    'lang_lookup' : LangMinion_prompt_lookup,
    'lang_gen_ielts_speak_test' : LangMinion_prompt_gen_ielts_speak_test
}
def func_text_preprocess_lang_gen_ielts_speak_test(text):
    if text:
        return text
    return 'random'
LangMinion_text_preprocess_dict = {
    'lang_gen_ielts_speak_test' : func_text_preprocess_lang_gen_ielts_speak_test
}

class OpenAILangMinionBackend():
    def __init__(self, model_name = "gpt-4.1", api_key = None, endpoint = None):
        from openai import AzureOpenAI
        from azure.identity import DefaultAzureCredential, get_bearer_token_provider
        self.model_name = model_name
        self.api_key = api_key
        if not self.api_key:
            raise ValueError("API key is not set")

        self.endpoint = endpoint
        if not self.endpoint:
            raise ValueError("Endpoint is not set")

        client = AzureOpenAI(
            api_key=self.api_key,  
            api_version="2024-10-21",
            azure_endpoint = self.endpoint
        )
        self.client = client

    def respond(self, prompt, text):
        print(f'respond(): respont text [{text}] with prompt [{prompt}]')
        message_list = []
        if prompt:
            message_list.append({"role": "system", "content": prompt})
        message_list.append({"role": "user", "content": text})
        completion = self.client.chat.completions.create(
            model=self.model_name,
            messages=message_list
        )
        ret = completion.choices[0].message.content
        print(f"OpenAILangMinionBackend.respond(): {ret}")
        return ret
    
    def can_handle_command(self, cmd):
        return cmd in LangMinion_prompt_dict
    
    def respond_command(self, cmd, text):
        prompt = ''
        if cmd in LangMinion_prompt_dict:
            prompt = LangMinion_prompt_dict[cmd]
        # print(f'respond_command(): cmd [{cmd}]-> prompt [{prompt}]')
        if cmd in LangMinion_text_preprocess_dict:
            text = LangMinion_text_preprocess_dict[cmd](text)
        return self.respond(prompt, text)