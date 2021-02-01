import html
from langdetect import detect, detect_langs
import re
import math
import aspell
import string

s = aspell.Speller('lang','es')
words_excluded = ['PSOE','PodemosCMadrid','PP', 'PartidoPopular','UPyD', 'Podemos', 'c\'s', 'Ciudadanos', 'IU','cs']
valid_chars = ['!','?','¡','¿','.'] + list(string.ascii_lowercase)

def convert_html_to_ascii(text):
    return html.unescape(text)

def remove_unicode_characters(text):
    return text.encode("utf-8","ignore").decode("utf-8")

def remove_long_words(text):
    return ' '.join([w for w in text.split() if len(w)<=20])

def is_spanish(text):
    result = True
    try:
        result = detect(text) == 'es'
    except:
        result = False
    return result

def remove_embedded_url(text):
    return re.sub(r'http\S+', '', text)

def remove_html_tag(text):
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', text)
    return cleantext

def remove_user_mentions(text):
    return re.sub('@[^\s]+','',text)

def remove_tweeter_specific(text):
    return remove_html_tag(remove_embedded_url(text))

def remove_consecutive_punctuation(text):
    candidates = [i for i,j in re.findall(r"((.)\2{3,})",text)]
    if candidates:
        for candidate in candidates:
            if candidate[0] in valid_chars:
                text = text.replace(candidate,candidate[0])
    return text

def correct_spelling(line):
    words = line.split()
    i = 0
    for word in words:
        if re.match('@[^\s]+',word):
            i+= 1
            continue
        if word not in s:
            has_ex_word = False
            for ex_word in words_excluded:
                if ex_word.lower() in word.lower():
                    has_ex_word = True
                    break
            if not has_ex_word:
                suggestions = s.suggest(word)
                if (len(suggestions) != 0):
                    words[i] = suggestions[0]
        i += 1
    return ' '.join(words)

def main():
    file_name = 'data/tweets-sample.txt'
    file_output_name = file_name[:-4] + '-preprocessed.txt'
    start_line = 1
    total_lines = 499    
    with open(file_name) as reader:
        mode = 'w'
        if start_line != 1:
            mode = 'a'
        with open(file_output_name,mode) as writer:
            writer.write('\n')
            lines = reader.readlines()
            while (start_line < len(lines)):
                line = lines[start_line]
                start_line += 1
                progress = math.floor(start_line/float(total_lines) * 100)
                if progress % 4 == 0:
                    print(progress)
                line = convert_html_to_ascii(line)
                line = remove_unicode_characters(line)
                line = remove_tweeter_specific(line)
                if not is_spanish(line):
                    continue
                line = remove_long_words(line)
                line = remove_consecutive_punctuation(line)
                line = correct_spelling(line)
                writer.write(line+'\n')

if __name__ == "__main__":
    main()