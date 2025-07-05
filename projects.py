import pandas as pd

def translation():
    data = pd.read_json('static/assets/morse_code.json', orient='index')
    to_translate = list(input('Word or phrase to translate: '))
    result = []
    for letter in to_translate:
        if letter in data.index:
            result.append(data[data.index == letter].values.item())
            result.append(' ')
        elif letter == ' ':
            result.append('/')
            result.append(' ')
        else:
            result.append('#')
            result.append(' ')
    answer = ' '.join(result)
    return answer
