def check_strings(s):
    if s.startswith('The'):
        return('Yes!')
    else:
        return('No!')
str1 = 'The'
str2 = 'Thumbs up'
str3 = 'Theatre can be boring'
print(check_strings(str1))
print(check_strings(str2))
print(check_strings(str3))