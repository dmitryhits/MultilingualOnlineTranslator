import requests
from bs4 import BeautifulSoup
from itertools import chain
import argparse


class Translator:
    def __init__(self):
        self.supported_languages = ["Arabic", "German", "English", "Spanish", "French", "Hebrew", "Japanese", "Dutch",
                                    "Polish", "Portuguese", "Romanian", "Russian", "Turkish"]
        self.current_target_language = 0
        self.target_languages = []
        self.source_language = 0
        self.input_word = ''
        self.content = ''
        self.translations = []
        self.examples = []
        parser = argparse.ArgumentParser(description=
                                         'This program print translations from target language (1st argument)'
                                         'to source language (2nd argument) '
                                         '"all" can be used to translate to all available langauges'
                                         )
        parser.add_argument('source_language')
        parser.add_argument('target_language')
        parser.add_argument('word')
        self.args = parser.parse_args()

    def get_word(self):
        # self.input_word = input('Type the word you want to translate:')
        self.input_word = self.args.word

    def get_target_languages(self):
        # i = int(input("Type the number of a language you want to translate to "
        #               "or '0' to translate to all languages:\n")) - 1
        target_language = self.args.target_language
        if target_language == 'all':
            self.target_languages = self.supported_languages
            i_source = self.target_languages.index(self.source_language.capitalize())
            self.target_languages.pop(i_source)
        else:
            if target_language.capitalize() in self.supported_languages:
                self.target_languages.append(target_language)
            else:
                print(f"Sorry, the program doesn't support {target_language}")

    def get_current_target_language(self, i_language):
        self.current_target_language = self.target_languages[i_language]

    def dialog(self):
        self.get_source_language()
        self.get_target_languages()
        self.get_word()

    def number_of_target_languages(self):
        return len(self.target_languages)

    def get_source_language(self):
        # i = int(input("Type the number of your language:\n")) - 1
        source_language = self.args.source_language
        if source_language.capitalize() in self.supported_languages:
            self.source_language = source_language
        else:
            print(f"Sorry, the program doesn't support {source_language}")

    def greetings(self):
        print("Hello, you're welcome to the translator. Translator supports:")
        for i, lang in enumerate(self.supported_languages):
            print(f"{i + 1}. {lang}")
        # print(file'You chose "{self.target_language}" as a language to translate "{self.input_word}".')

    def get_page(self):
        headers = {'User-Agent': 'Mozilla/5.0'}
        fromto = f'{self.source_language.lower()}-{self.current_target_language.lower()}'
        url = f"https://context.reverso.net/translation/{fromto}/{self.input_word}"
        try:
            r = requests.get(url, headers=headers)
        except requests.exceptions.ConnectionError:
            print('Something wrong with your internet connection')
        if r:
            # print(r.status_code, 'OK')
            self.content = r.content
        else:
            print(f"Sorry, unable to find {self.input_word}")
            exit()

    def get_info(self):
        soup = BeautifulSoup(self.content, 'html.parser')
        self.translations = [
            list(t.stripped_strings)[0] for t in soup.find_all('a', {'class': 'translation'})
            if not list(t.stripped_strings)[0] == 'Translation'
        ]
        # Get all translated examples
        target_language_example = [t.get_text().strip().lower()
                                   for t in soup.find_all('div', {'class': ['trg ltr', 'trg rtl arabic', 'trg rtl']})]
        source_language_example = [t.get_text().strip().lower() for t in soup.find_all('div', {'class': 'src ltr'})]

        self.examples = list(chain(*[example_pair for example_pair
                                     in zip(source_language_example, target_language_example)]))

    def pretty_print(self):
        n_examples = 1
        language = self.current_target_language.capitalize()

        print()
        print(f"{language} Translations:")
        # print(self.translations)
        for i_example in self.translations[:n_examples]:
            print(i_example)
        print()
        print(f"{language} Examples:")
        for i, example in enumerate(self.examples[:n_examples * 2]):
            # example = example.replace(' .', '.')
            # example = example.replace(' ,', ',')
            if i % 2:
                print(example)
                # print()
            else:
                print(f'{example}')

    def get_filename(self):
        return self.input_word + '.txt'

    def pretty_write(self, file):
        n_examples = 1
        language = self.current_target_language.capitalize()

        file.write('\n')
        file.write(f"{language} Translations:\n")
        # file.write(self.translations)
        for i_example in self.translations[:n_examples]:
            file.write(i_example + '\n')
        file.write('\n')
        file.write(f"{language} Examples:\n")
        for i, example in enumerate(self.examples[:n_examples * 2]):
            if i % 2:
                file.write(example + '\n')
            else:
                file.write(f'{example}\n')


if __name__ == '__main__':
    translate = Translator()
    translate.greetings()
    translate.get_source_language()
    translate.get_target_languages()
    translate.get_word()
    filename = translate.get_filename()
    with open(filename, 'w', encoding='utf-8') as f:
        for i in range(translate.number_of_target_languages()):
            translate.get_current_target_language(i)
            translate.get_page()
            translate.get_info()
            translate.pretty_print()
            translate.pretty_write(f)
