from sandman.model import Model


class SCourse(Model):
    __tablename__ = 'courses'
    __endpoint__ = 'courses'
    __methods__ = ('GET')


class SCourseOffering(Model):
    __tablename__ = 'course_offerings'
    __endpoint__ = 'course_offerings'
    __methods__ = ('GET')
