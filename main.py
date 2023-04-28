from dotenv import load_dotenv
load_dotenv()
import os
import sys
import time
import json
import ai
import twitter

responses = json.loads(open('responses.json').read())


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


while True:
    start = time.perf_counter()
    print('Generating fact...')
    result = ai.generateFact(responses)
    if len(result) > 280:
        result = result[:280]
    print(f"Generated in {time.perf_counter() - start} seconds\n")
    responses.append(result)
    print("Dumping responses...")
    json.dump(responses, open('responses.json', 'w'), indent=4)
    print(f"Dumped responses in {time.perf_counter() - start} seconds\n")
    twitter.sendTweet(result.strip())
    print(result.strip())
    print("\n\n\n")
    print("Waiting for 1 hour")
    countdown(3550)
