def get_prompt_for_next_word(current_sentence: str, style: str, mood: str, refresh=False, current_words=None):
    # word_prompt = f"give me 7 options to continue the next word of the sentence: '{current_sentence}...'," \
    #                       f" the output should be in the format: 'word_1'\n'word_2'\n'word_3' and so on." \
    #                       f"ASSURE YOU ONLY PREDICT THE NEXT WORD!"

    if refresh:
        refresh_prompt1 = f"Additionally, you may not use any of the following words: {current_words}, so be creative. Do not repeat words either, and make sure only single words are provided, not phrases."
        refresh_prompt2 = f" and may not contain any of these given words: {current_words}."
    else:
        refresh_prompt1 = ""
        refresh_prompt2 = ""

    word_prompt = f"""Given a sentence fragment, your task is to predict the immediate next word that logically follows. Provide seven distinct and plausible predictions, each being a single word that could naturally continue the sentence. This exercise aims to explore the variety of possible directions the sentence could go with just the next word. 
    Your suggestions should be in the style and theme of a {style} and your current emotion is {mood}. {refresh_prompt1}
    Sentence Fragment: {current_sentence}
    Predicted Next Words:
    1.
    2.
    3.
    4.
    5.
    6.
    7.

    Note: Each prediction must consist of exactly one word, focusing on the immediate and logical continuation of the provided sentence fragment{refresh_prompt2}.
    """

    return word_prompt


def get_prompt_for_next_phrases(current_sentence: str, style: str, mood: str, refresh=False, current_phrases=None):
    # sentence_prompt = f"give me 5 options to continue the next 3 words of the sentence: '{current_sentence}...'," \
    #                       f" the output should be in the format: '...sentence 1'\n '...sentence 2' and so on. " \
    #                       f"ASSURE YOU ONLY PREDICT THE NEXT 3 WORDS!"

    if refresh:
        refresh_prompt1 = f"Additionally, you may not use any of the following phrases{current_phrases}, so be creative. PLease do not repeat phrases either."
        refresh_prompt2 = f" and please ensure that  none of these phrases {current_phrases} are used"
    else:
        refresh_prompt1 = ""
        refresh_prompt2 = ""

    sentence_prompt = f"""Given a sentence fragment, your task is to provide the immediate next three words, no more, no less. It is crucial to adhere strictly to this three-word limit to ensure precision in continuation predictions. Provide five distinct and plausible continuations, ensuring each set of three words offers a different potential direction or meaning. This exercise aims to explore the variety of possible sentence continuations within the precise constraint of three words.
    Your suggestions should be in the style and theme of a {style} and your current emotion is {mood}. {refresh_prompt1} 
    Sentence Fragment: {current_sentence}

    Predicted Continuations:
    1.
    2.
    3.
    4.
    5.

    Remember: Each continuation must consist of exactly three words, focusing on the immediate continuation of the provided sentence fragment{refresh_prompt2}.
    """
    return sentence_prompt
