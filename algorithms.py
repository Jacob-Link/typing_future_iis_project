# pip install -q -U google-generativeai
import google.generativeai as genai
import prompts
import random


def process_gemini_response(x):
    sentences = x.split("\n")
    sentences = [x.replace("*", "") for x in sentences]  # drop bold

    if len(sentences[0].split(" ")) > 2:  # phrase prediction
        sentences = ["..." + x[3:] for x in sentences]  # drop the index we defined in the prompt...
    else:
        sentences = [x[3:] for x in sentences]  # drop the index we defined in the prompt...

    # drop the dot at the end of each sentence if appears
    res = []
    for sentence in sentences:
        if sentence[-1] == ".":
            res.append(sentence[:-1])
        else:
            res.append(sentence)

    return res


def prompt_model(model: genai, prompt: str) -> list:
    generation_response = model.generate_content(prompt)

    count = 0
    try:
        while (len(generation_response.parts) == 0) and (count < 3):  # model returned empty response, allow 3 retries
            generation_response = model.generate_content(prompt)
            count += 1
        result_list = process_gemini_response(generation_response.text)
    except:
        return []

    return result_list


def get_word_predictions(model: genai, current_sentence: str, style: str, mood: str, refresh=False, words=None,
                         num_words=7):
    prompt = prompts.get_prompt_for_next_word(current_sentence, style, mood, refresh, words)
    res = prompt_model(model, prompt)

    if len(res) == 0:  # conflict with gemini safety
        res = [f"Error_{i}" for i in range(num_words)]

    return res


def get_sentence_predictions(model: genai, current_sentence: str, style: str, mood: str, refresh=False, phrases=None,
                             num_phrases=5):
    prompt = prompts.get_prompt_for_next_phrases(current_sentence, style, mood, refresh, phrases)
    res = prompt_model(model, prompt)

    if len(res) == 0:  # conflict with gemini safety
        res = [f"Error_{i}" for i in range(num_phrases)]

    return res


def get_first_word_predictions(app_style_index: int):
    apps = ["facebook", "whatsapp", "google", "linkedin"]
    app_style = apps[app_style_index]

    if app_style == "google":
        return ["Youtube", "Facebook", "Weather", "Gmail", "Translate", "Chatgpt"]  # top searches 2023

    if app_style == "facebook":
        return ["The", "In", "What", "It", "This", "I", "There"]

    if app_style == "whatsapp":
        return ["Hello", "How", "Why", "What", "Are", "I", "There"]

    if app_style == "linkedin":
        return ["Celebrating", "Wow", "Why", "What", "Are", "I", "There"]


def get_first_sentence_predictions(app_style_index: int, mood: str):
    apps = ["facebook", "whatsapp", "google", "linkedin"]
    app_style = apps[app_style_index]

    if (mood in ["funny", "happy"]) and (app_style == "whatsapp"):
        return ["Hey there...",
                "Whats up?",
                "Knock knock...",
                "What a beautiful...",
                "Thats amazing...",
                "Good stuff!"]

    if (mood in ["neutral", "serious"]) and (app_style == "whatsapp"):
        return ["Hey there...",
                "Whats up?",
                "I approve...",
                "That is interesting...",
                "I'm not sure...",
                "That's ok."]

    if (mood in ["sad", "angry"]) and (app_style == "whatsapp"):
        return ["No way!",
                "I'm struggling with...",
                "Can you help...",
                "That's not alright.",
                "How could you...",
                "That's not ok."]

    if (mood in ["funny", "happy"]) and (app_style == "facebook"):
        return ["Greetings Facebook friends!",
                "Hello world!",
                "Hi everyone...",
                "Knock knock...",
                "Happy birthday..."]

    if (mood in ["neutral", "serious"]) and (app_style == "facebook"):
        return ["I don't usually...",
                "Hello world!",
                "Hi everyone...",
                "What does everyone think...",
                "Happy birthday...",
                "How do you feel..."]

    if (mood in ["sad", "angry"]) and (app_style == "facebook"):
        return ["I don't usually...",
                "How is it possible...",
                "I am furious...",
                "Why the hell...",
                "Sad birthday...",
                "How do you feel..."]

    if (mood in ["funny", "happy"]) and (app_style == "linkedin"):
        return ["Greetings LinkedIn users!",
                "I am proud...",
                "I am delighted...",
                "Pleased to announce...",
                "Happy to share..."]

    if (mood in ["neutral", "serious"]) and (app_style == "linkedin"):
        return ["Hello LinkedIn users!",
                "I dont usually...",
                "What does everyone think...",
                "It is interesting...",
                "Would like to share..."]

    if (mood in ["sad", "angry"]) and (app_style == "linkedin"):
        return ["I don't usually...",
                "How is it possible...",
                "I am furious...",
                "Who thought of...",
                "I'm disappointed...",
                "Unfortunately, today..."]

    if app_style == "google":
        return ["How to...",
                "Whats the...",
                "Why do...",
                "Are the...",
                "Where are...",
                "Good stuff!"]


def get_words_and_phrases_drop_dups(words: list, phrases: list):
    """
    gets 2 lists of strings, returns the lists after dropping
    """
    words_to_drop = []
    for word in words:
        if word in phrases:
            words_to_drop.append(word)

    # for word in words_to_drop:
    #     words.remove(word)  # this modifies the original list
    words = [x for x in words if x not in words_to_drop]

    return words, phrases


def get_random_words_for_refresh(num_words: int):
    top_words_wikipedia_filtered = ['The', 'In', 'He', 'It', 'On', 'This', 'A', 'She', 'After', 'See', 'As', 'They',
                                    'His', 'At', 'People', 'There', 'However', 'During', 'History', 'For', 'When',
                                    'These', 'From', 'According', 'By', 'With', 'Other', 'While', 'Early', 'One',
                                    'Some', 'Since', 'List', 'Career', 'Her', 'Although', 'New', 'An', 'Its']
    return random.sample(top_words_wikipedia_filtered, k=num_words)


def get_random_phrases_for_refresh(num_phrases: int):
    top_phrases_wikipedia_filtered = ['According to the', 'Members of the', 'As of the', 'In addition to', 'One of the',
                                      'It is a', 'It is the', 'The median age', 'The average household', 'He was a',
                                      'He was the', 'The median income', 'As a result,', 'It is also', 'There is a',
                                      'It was the', 'He was also', 'In the early', 'Most of the', 'The population was',
                                      'At the end', 'Some of the', 'It has been', 'This is a', 'Due to the',
                                      'Early life and', 'At the time', 'The film was', 'It is located']

    return random.sample(top_phrases_wikipedia_filtered, k=num_phrases)
