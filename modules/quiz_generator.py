"""
Quiz Generator (Safe Version)
Always returns valid output
"""

import random
import re
import spacy

class QuizGenerator:
    def __init__(self):
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except:
            self.nlp = None
            print("⚠ spaCy model not loaded – quiz will be simplified")

    def generate_mcq(self, sentences, num_questions=5):
        questions = []

        if not sentences:
            return questions

        for sentence in sentences:
            if len(questions) >= num_questions:
                break

            if len(sentence.split()) < 8:
                continue

            words = [w for w in sentence.split() if len(w) > 4]
            if not words:
                continue

            answer = random.choice(words)
            question = sentence.replace(answer, "_____")

            options = random.sample(words, min(3, len(words)))
            if answer not in options:
                options.append(answer)

            random.shuffle(options)

            questions.append({
                "question": question,
                "options": options,
                "correct_answer": answer
            })

        return questions

    def generate_short_answer(self, sentences, num_questions=3):
        questions = []

        for sentence in sentences:
            if len(questions) >= num_questions:
                break

            if " is " in sentence.lower():
                questions.append({
                    "question": "Explain: " + sentence.split(" is ")[0],
                    "answer": sentence
                })

        return questions
