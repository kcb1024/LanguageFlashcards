# -*- coding: utf-8 -*-

# Duolingo API -- see https://github.com/KartikTalwar/duolingo
import duolingo as duo 

# Package for CSV files
import csv 

# List of languages, including native English
langs_wEnglish = ['English','Irish', 'Greek', 'German', 'French', 'Welsh', 'Spanish', 'Italian']

def fetchUserInfo(filepath = 'C:/Users/karen/Documents/Python Scripts/duo_userinfo.txt'):
    """Gets username and password out of a text file """
    f = open(filepath, 'r')
    info = f.read()
    [username, password] = info.splitlines()
    return username, password

def buildDict():
    """Pull vocabulary from Duolingo account and format it into a CSV file """
    #settings for dictionary ------------------------------------
    #this determines if conjugated verbs (e.g. he drinks, you are) 
    #are part of the dictionary
    conjugations_allowed = False
    
    # Not currently used
    web_access = False
    
    
    #list of pronouns
    pronouns = {'English': ['I','you','she','he','it','we','they'],
                'French': ['je','tu','il','elle','on','nous','vous','ils','elles']}
    
    #login information for Duolingo
    username, password = fetchUserInfo()

    #native language for flashcards
    native_language = 'English'
    #log into Duolingo and create the user object
    user = duo.Duolingo(username, password)
    #get the list of languages that I'm studying
    lang_wo_abbrev = user.get_languages() #lang_wo_abbrev e.g. ['French', 'German']
    #build a dictionary linking language abbreviations (e.g. 'fr') to languages 
    #(e.g. 'French')
    lang_abbrev = {}
    for i in lang_wo_abbrev:
        lang_abbrev[i] = user.get_abbreviation_of(i)
    #lang_abbrev example = {'French':'fr', 'German':'de'}
    
    #start building a dictionary where the dict key is in the native language
    #and values are in target languages
    native_dict = {}
    #get the abbreviation of the native language, e.g. 'en' for English
    native_abbrev = user.get_abbreviation_of(native_language)
    
    #for every language, get the words that the user has learned   
    #for lang in lang_wo_abbrev:
    langlist = langs_wEnglish[1:]
    for lang in lang_abbrev.keys():
        print lang
        #make sure that we're on the right language
        #in Duolingo, the API only works with one language at a time
        #and must switch to that language before it can pull data about 
        #words, skills, etc learned in that language
        user._switch_language(lang_abbrev[lang])
        #create a temporary dict with all the words learned in this language
        temp_dict = user.get_known_words(lang_abbrev[lang])
        #now we're going to start working on the master dictionary
        #iterate through the known words for each language
        for word in temp_dict:
            #get translation, which is a dictionary entry
            #example: user.get_translations(['prynhawn'],'en','cy') returns
            #{u'prynhawn': [u'Afternoon']}
            #b/c prynhawn means afternoon in Welsh ('cy')
            translation_entry = user.get_translations([word], 
                                                      native_abbrev,
                                                      lang_abbrev[lang])
            #now we want to process the data, since a word in the native language
            #(usually English) might have multiple definitions in the 
            #target language
            key = translation_entry.keys()
            #make a list of all translations of the word
            #example: [u'Welcome', u"You're welcome", u'You are welcome'] = 
            #         translation_entry['croeso']
            native_translation = translation_entry[key[0]]
            #now we want to go through the definitions
            #if the native word is already in the dictionary, we'll just add the
            #target language translation. However, if the native word isn't in
            #the dictionary, we'll make an entry for that
            #start by iterating through the keys
            for entry in native_translation:
                #if there's an entry for the native word in the dictionary
                if entry in native_dict:
                    #if there's already an entry in this target language 
                    #in the dictionary, and we're adding a second translation 
                    #in the same target language
                    if lang in native_dict[entry]:
                        native_dict[entry][lang] += key
                    #if there's not already a translation in the target language,
                    #add one
                    else:
                        native_dict[entry][lang] += key

                #if the native word isn't in the dictionary, add it maybe
                else:
                    #see if we want to add the entry
                    if conjugations_allowed:
                        native_dict[entry][lang] = key
                    #if we're not allowing conjugations
                    else:
                        pron = pronouns[native_language]
                        c = len(pron)
                        for p in pron:
                            if str('(' + p ) in entry:
                                c = 0
                        #if there's no pronoun in the entry, add the entry
                        if c == len(pron):
                            native_dict[entry] = {}
                            native_dict[entry][lang] = key
    
    #write the data to a file called dictionary.txt in the same directory
    #as the python file, because that makes my life easier
    ctr = 0
    with open('dict.csv', 'wb') as csvfile:
        w = csv.writer(csvfile, delimiter=',')
        #write header row
        w.writerow(langs_wEnglish)
        for item in native_dict.items():
            ctr = 0
            line = ['']*(len(langlist) + 1)
            line[0] = item[0] #English
            for i in langlist:
                ctr+=1
                if(i in item[1]):
                    line[ctr] = writeMultDefs(item[1][i])
            w.writerow(line)    
    return

def writeMultDefs(entry):
    """ Writes multiple definitions of a word to a CSV file """
    out = ''
    l = len(entry)
    if (l > 1):
        for i in range(l - 1):
            out += str(entry[i]) + ';'
        out += str(entry[i+1])
    else:
        out = str(entry[0])
    return out

    
def buildCards(filename = 'dict.csv'):
    """ Reads data from the CSV file and converts it into a list """
    ll = []
    dictin = csv.DictReader(open(filename))
    c = 0
    for row in dictin:
        ll += [row]
        c+=1
    return ll

def study(filename = 'dict.csv', target_language = ''):
    """ Function letting the user study languages
    inputs
    - filename: name of dictionary csv file 
    - target_language: language that user is studying
    """
    data = buildCards(filename)
    user_in = ''
    ctr = 0
    exit_code = 'X'
    while(user_in != exit_code):
        # Check to see if entry in target language
        if (data[ctr][target_language] != ''):
            # Iterate through languages
            for i in langs_wEnglish:
                # English
                if (i == 'English'):
                    print 'English: ' + data[ctr][i]
                # Language that is not English
                else:
                    # Check to see if there's an entry for this language
                    if (data[ctr][i] != ''):
                        # If there's an entry, print it
                        print i + '?'
                        user_in = raw_input("Got it?")
                        print data[ctr][i]
                # Check to see if user wants to exit
                if (user_in == exit_code):
                    break
#        print '\n'
        ctr += 1
    return