from bs4 import BeautifulSoup
from urllib2 import urlopen
import re

def get_tags():
    html = urlopen('http://catalog.oregonstate.edu/CourseDescription.aspx?level=undergrad').read()
    soup = BeautifulSoup(html)
    table = soup.find(id='ctl00_ContentPlaceHolder1_dlSubjects')
    cats_text = table.find_all('a')
    cat_re = re.compile(r'.+\((.+)\).*')

    tags = set()
    for a in cats_text:
        if not a.text.startswith('OS/'):
            match = cat_re.match(a.text)
            if match:
                tag = match.groups()[0].upper()
                print tag
                if not tag in tags:
                    print "adding tag {0}".format(tag)
                    tags.add(tag)

    with open('tags.txt', 'w') as f:
        for tag in tags:
            f.write(tag + ',')
