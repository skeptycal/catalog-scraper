from bs4 import BeautifulSoup
import re
import sys
import urllib2

from models import session, Course, CourseOffering


def get_co_type(item):
    k, v = item
    if k == 'pass_nopass':
        return (k, bool(v))
    try:
        item = (k, int(v))
    except ValueError:
        pass
    return (k, v)

def get_all_courses():
    f = open('tags.txt', 'r')
    tags = f.read().split(',')[:-1]
    f.close()

    subj_url = 'http://catalog.oregonstate.edu/CourseList.aspx?subjectcode=%s&level=undergrad&campus=corvallis'
    base_url = 'http://catalog.oregonstate.edu/%s'

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
                            url=base_url % course.attrs.get('href'))
            session.add(course)
            session.commit()
            print 'Added %s %s to db!' % (c.group('num'), c.group('title'))
            print


def get_all_course_offerings():
    course_offering_ids = [cid[0] for cid in session.query(CourseOffering.id).all()]
    courses = (session.query(Course)
                .filter(~Course.id.in_(course_offering_ids))
                .all())
    count, end = 1, len(courses)
    for course in courses:
        get_course_offering(course, count, end)
        count += 1


def get_course_offering(course, count, end):
    fields = ['course_id', 'term', 'crn', 'section', 'pass_nopass',
              'instructor', 'day_time', 'location', 'campus', 'c_type',
              'status', 'cap', 'current', 'available', 'wl_cap', 'wl_current',
              'wl_available', 'section_title', 'fees', 'restrictions',
              'comments']

    html = urllib2.urlopen(course.url).read()
    soup = BeautifulSoup(html)

    table = soup.find(id='ctl00_ContentPlaceHolder1_SOCListUC1_gvOfferings')
    if not table:
        # No course offerings found for that course.
        return

    trs = table.find_all('tr')[1:]
    print ('Downloading %d Course Offerings for: %s %s %s (%s) (%d/%d)' %
            (len(trs), course.tag, course.num, course.title, course.credits,
             count, end))

    for tr in trs:
        elems = tr.find_all('font')
        # Get rid of 'Credits' field.
        del elems[3]
        elem_vals = [course.id] + [elem.text for elem in elems]
        mapped_fields = dict(map(get_co_type, zip(fields, elem_vals)))
        course_offering = CourseOffering(**mapped_fields)
        session.add(course_offering)
        session.commit()


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'initdb':
        from models import init_db
        init_db()

    get_all_courses()
    get_all_course_offerings()
