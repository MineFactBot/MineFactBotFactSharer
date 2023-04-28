import sys
import time
from urllib.parse import quote
import os
import openai
from datetime import datetime
from colorama import init as colorama_init
from colorama import Fore
from colorama import Style
from youdotcom import Chat
from ratelimit.exception import RateLimitException

colorama_init()

openai.api_key = os.getenv("OPENAI_API_KEY")
messages = [{
    "role": "system",
    "content": "You are an AI Model that gives one random interesting Minecraft fact about any topic (for example "
               "mechanics, youtubers, textures, models etc...) for twitter so mention related people everytime (for "
               "example if it is about textures mention a texturer from Mojang or if you say someone's name mention "
               "it), use good tags. Don't repeat"
               "yourself. Full text's length should be less than 280 characters. Generate only one fact. Today is "
               f"{datetime.now().strftime('%A')}. Facts needs to be true. Just generate true facts"
}]

checkMessage = [{
    "role": "system",
    "content": "There is an AI that generates interesting Minecraft fact tweets. But sometimes it generates same "
               "thing twice. User will give you 8 tweets and your mission is detecting if "
               "new tweet is"
               "already generated before. You will say True if new fact is already generated before "
               "You will say False if "
               "new fact is not already generated before. Just say True or False. And explain which fact "
               "is same with new tweet."
}]

shorterMessage = [{
    "role": "system",
    "content": "You are an AI model that regenerate shorter version of given tweet. Tweet's length should be shorter "
               "than 280 characters"
}]

realMessage = [{
    "role": "system",
    "content": "There is a twitter bot that shares minecraft facts hourly. But sometimes it generates false facts. "
               "Given text has a minecraft fact. Return \"True\" if fact is real Return \"False\" if fact is not real."
}]

mentionerMessage = [{
    "role": "system",
    "content": "You are an AI model that replace names with twitter mentions in given text \nReturn replaced version "
               "of text"
}]

plainerMessage = [{
    "role": "system",
    "content": "Write given tweet as plain text remove hashtags"
}]


def countdown(t, step=1, msg='sleeping'):  # in seconds
    """
    Counts down from t to 0
    :param t: The time to count down from
    :param step: The step to count down
    :param msg: The message to print
    """
    pad_str = ' ' * len('%d' % step)
    for i in range(t, 0, -step):
        print(f'\r{msg.capitalize()} for the next {i} seconds {pad_str}', end='')
        sys.stdout.flush()
        time.sleep(step)
    print(f'Done {msg} for {t} seconds!  {pad_str}')


def generateFact(responses):
    """
    Generates a random fact
    :param responses: The responses to check against
    :return: The generated fact
    """
    print("Generating first fact...", end=" ")
    messages_ = messages[::-1][::-1]
    response = mentioner(textShorter(prompt(messages_, 2048)))
    print(response)
    plain = plainer(response)
    if realChecker(plain) and realCheckerLayer2(plain) and realCheckerLayer3(plain) and checkFact(plain, responses):
        return response
    else:
        checkCounter = 1
        while True:
            checkCounter += 1
            print(f"Generating fact {checkCounter}...", end=" ")
            response = prompt(messages_, 2048)
            response = mentioner(textShorter(response))
            print(response)
            messages_.append({
                "role": "assistant",
                "content": response
            })
            plain = plainer(response)
            if realChecker(plain) and realCheckerLayer2(plain) and realCheckerLayer3(plain) and checkFact(plain,
                                                                                                          responses):
                return response


def mentioner(text):
    messages_ = mentionerMessage[::-1][::-1]
    messages_.append({
        "role": "user",
        "content": text
    })
    return prompt(messages_, 2048)


def plainer(text):
    messages_ = plainerMessage[::-1][::-1]
    messages_.append({
        "role": "user",
        "content": text
    })
    return prompt(messages_, 2048)


def generateEightSequence(responses, idx):
    txt = ""
    for i in range(0, 8):
        try:
            txt += f"{i + 1}- {responses[idx + i]} \n"
        except IndexError:
            break
    return txt


def checkFact(fact, responses):
    """
    Checks if the fact is already generated
    :param fact: The fact to check
    :param responses: The responses to check against
    :return: True if the fact is not generated before, False if it is
    """
    result = ""
    results = []
    for i in range(0, len(responses), 8):
        checkMessage_ = [d.copy() for d in checkMessage]
        checkMessage_[0]["content"] += "\n\n New fact: " + fact + "\n\n"
        messages_ = checkMessage_
        messages_.append({
            "role": "user",
            "content":
                f"""
                {generateEightSequence(responses, i)}
                """
        })
        result = prompt(messages_, 2048)
        if "true" in result.lower():
            results.append(True)
            break
        elif "false" in result.lower():
            results.append(False)
    cond = not any(results)
    if not cond:
        print(f"{Fore.RED}Fact is generated before!{Style.RESET_ALL} - {result}")
    return cond


def prompt(msgs, max_token):
    """
    Prompts the user
    :param msgs: The messages to prompt
    :param max_token: The max tokens to prompt
    :return: The response
    """
    while True:
        try:
            result = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=msgs,
                max_tokens=max_token,
                temperature=0.7,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0
            )
            return result.choices[0].message.content
        except Exception as e:
            msgs = msgs[1:]
            print("Error: " + str(e))


def textShorter(text):
    if len(text) > 280:
        messages_ = shorterMessage[::-1][::-1]
        messages_.append({
            "role": "user",
            "content": text
        })
        result = prompt(messages_, 2048)
        if len(result) > 280:
            return textShorter(result)
        return result
    return text


def realChecker(fact):
    messages_ = realMessage[::-1][::-1]
    messages_.append({
        "role": "user",
        "content": fact
    })
    result = prompt(messages_, 2048)
    if "true" in result.lower():
        return True
    print(f"{Fore.RED}False fact detected(Layer 1)!{Style.RESET_ALL}")
    return False


def realCheckerLayer2(fact):
    def convertToQuestion(fact_):
        msgs = [{
            "role": "system",
            "content": "Write given tweet that give a Minecraft information as yes/no question. Remove hashtags. "
                       "Remove other questions "
                       "that asked to users, but keep all information about Minecraft"
        },
            {
                "role": "user",
                "content": fact_
            }]
        response = prompt(msgs, 2048)
        return response

    def askTheQuestion(question):
        msgs = [{
            "role": "system",
            "content": "Answer the question about Minecraft with True or False, true means yes, false means no"
        },
            {
                "role": "user",
                "content": question
            }]
        response = prompt(msgs, 2048)
        return response

    q = convertToQuestion(fact)
    a = askTheQuestion(q)
    if "true" in a.lower():
        return True
    print(f"{Fore.RED}False fact detected(Layer 2)!{Style.RESET_ALL}")
    return False


def realCheckerLayer3(fact):
    def convertToQuestion(fact_):
        msgs = [{
            "role": "system",
            "content": "Write given tweet that give a Minecraft information as yes/no question. Remove hashtags. "
                       "Remove other questions "
                       "that asked to users, but keep all information about Minecraft"
        },
            {
                "role": "user",
                "content": fact_
            }]
        response = prompt(msgs, 2048)
        return response

    def askTheQuestion(question):
        while True:
            try:
                chat = Chat.send_message(message=quote(
                    f"{question} Answer the question about Minecraft with True or False, true means yes, false means no",
                    safe=""), api_key="4Y4BNYK7NZV2QKPRG7A07VAPBXCMH902WVG")
                break
            except RateLimitException:
                countdown(60, msg="Waiting rate limit")
            except Exception:
                pass
        return chat["message"]

    q = convertToQuestion(fact)
    a = askTheQuestion(q)
    if "true" in a.lower():
        return True
    else:
        print(f"{Fore.RED}False fact detected(Layer 3)!{Style.RESET_ALL}")
        return False
