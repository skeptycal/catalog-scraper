from bs4 import BeautifulSoup
import re
import sys
import urllib2

from models import session, Course, CourseOffering


def get_all_courses():
    f = open('tags.txt', 'r')
    tags = f.read().split(',')[:-1]
    f.close()

    subj_url = 'http://catalog.oregonstate.edu/CourseList.aspx?subjectcode=%s&level=undergrad&campus=corvallis'

    for tag in tags:
        url = subj_url % tag
        html = urllib2.urlopen(url).read()
        soup = BeautifulSoup(html)

        table = soup.find(id='ctl00_ContentPlaceHolder1_dlCourses')
        courses = table.find_all(id=re.compile('ctl00_ContentPlaceHolder1_dlCourses_ctl.*_hlCourseTitle'))

        _course_re = re.compile(r'\w+ (?P<num>\d+)(?P<type>(H|NC|X))? (?P<title>(.+ )+)\((?P<credits>.+)\)')
        course_ids = [int(course.text.split(' ')[1].strip('HNCX')) for course in courses]
        existing_course_ids = (session.query(Course.num)
                                .filter(Course.num.in_(course_ids))
                                .filter(Course.tag==tag).all())
        existing_course_ids = set(cid[0] for cid in existing_course_ids)

        for course in courses:
            c = _course_re.match(course.text)
            if int(c.group('num').strip('HNCX')) in existing_course_ids:
                print '%s already in db!' % course.text
                continue
            course = Course(num=c.group('num'),
                            title=c.group('title'),
                            credits=c.group('credits'),
                            specialty=c.group('type') or '',
                            tag=tag,
                            url=course.href)
            session.add(course)
            session.commit()
            print 'Added %s %s to db!' % (c.group('num'), c.group('title'))
            print


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'initdb':
        from models import init_db
        init_db()

    get_all_courses()
