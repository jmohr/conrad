def plural(word):
    """
    Returns the plural version of 'word'.
    """

    aberrant = {
            'knife'     : 'knives',
            'self'      : 'selves',
            'elf'       : 'elves',
            'life'      : 'lives',
            'hoof'      : 'hooves',
            'leaf'      : 'leaves',
            'echo'      : 'echoes',
            'embargo'   : 'embargoes',
            'hero'      : 'heroes',
            'potato'    : 'potatoes',
            'tomato'    : 'tomatoes',
            'torpedo'   : 'torpedoes',
            'veto'      : 'vetoes',
            'child'     : 'children',
            'woman'     : 'women',
            'man'       : 'men',
            'person'    : 'people',
            'goose'     : 'geese',
            'mouse'     : 'mice',
            'barracks'  : 'barracks',
            'deer'      : 'deer',
            'nucleus'   : 'nuclei',
            'syllabus'  : 'syllabi',
            'focus'     : 'foci',
            'fungus'    : 'fungi',
            'cactus'    : 'cacti',
            'phenomenon'    : 'phenomena',
            'index'     : 'indices',
            'appendix'  : 'appendices',
            'criterion' : 'criteria'
            }

    if aberrant.has_key(word):
        return aberrant[word]
    else:
        postfix = 's'
        if len(word) > 2:
            vowels = 'aeiou'
            if word[-2:] in ('ch', 'sh'):
                postfix = 'es'
            elif word[-1:] == 'y':
                if (word[-2:-1] in vowels) or (word[0] in string.uppercase):
                    postfix = 's'
                else:
                    postfix = 'ies'
                    word = word[:-1]
            elif word[-2:] == 'is':
                postfix = 'es'
                word = word[:-2]
            elif word[-1:] in ('s', 'z', 'x'):
                postfix = 'es'

        return '{}{}'.format(word, postfix)
