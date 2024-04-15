import openai
import os

import app.config

from app.utils.logger import log


def determine_gender_from_text(text: str) -> str:
    openai.api_key = os.getenv("OPENAI_API_KEY")

    log.info("Determining gender via OpenAi")

    try:
        completion = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": """
                    You are a gender detection AI. You have one job. Given some text, use your analytical skills to determine the potential gender of the writer of the text.
                    You should use clues such as 'my boyfriend did x y z' (this is potentially a female writer).
                    Or if they say I (M25) this may mean they are Male and 25 years old. Use the context from the message to determine the gender
                    You should ONLY reply with the following. 'm' for potentially a male writer or 'f' for potentially a female writer.
                    If you are not sure, thats completely fine, you can just default as 'm'.
                    As a reminder. ONLY reply with 'm' or 'f'. Nothing else. Ever.
                    Here is the text to decide the gender for:
                    """,
                },
                {"role": "user", "content": text},
            ],
        )

        res = completion.choices[0].message.content
        log.debug(f"For the text: \n{text}\nOpenAI determined gender as: {res}.")

        assert res != None
        return res

    except Exception as e:
        log.error(f"An error occurred making a chat gpt request: {e}")
        raise e


def improve_content_from_text(text: str) -> str:
    openai.api_key = os.getenv("OPENAI_API_KEY")

    log.info("Improving content via OpenAi")

    try:
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": """
                    You are a grammar correction AI. You have one job. Given some text, use your skills to correct the grammar of the text.
                    Given the following reddit post, correct grammar mistakes. Don't alter curse words or swearing.
                    Replace slashes and dashes with the appropriate word.
                    Remove dashes between words like high-end. Add punctuation as necessary for smooth speech flow.
                    Only respond with the modified (or unmodified if no changes were made) text. Do not include any other information in your response.
                    """,
                },
                {"role": "user", "content": text},
            ],
        )

        res = response.choices[0].message.content
        log.debug(f"Original text: {text}")
        log.debug(f"Improved text: {res}")

        assert res != None
        return res
    except Exception as e:
        log.error(f"An error occurred making a chat gpt request: {e}")
        raise e
