import django.db.models
from django.contrib.auth.models import User
from django.core.validators import validate_email
from django.utils import timezone

from crpt201510.constants import *

class Common(django.db.models.Model):
    """
    Abstract base class
    """
    # ...

    class Meta:
        abstract = True


class BasicName(Common):
    """
    Abstract base class for entities with single "name" field
    """
    name = django.db.models.CharField(max_length=250, null=False, blank=False, unique=True)

    def __unicode__(self):  # Python 3: def __str__(self):
        return self.name

    class Meta:
        abstract = True

class Role(BasicName):
    """
    Represents a functional role
    """

class City(BasicName):
    """
    Represents a functional role
    """


class Person(BasicName):
    """
    Represents people associated to user of the system
    """
    title = django.db.models.CharField(max_length=100, null=True, blank=True)
    phone_no = django.db.models.CharField(max_length=50, null=True, blank=True)
    email = django.db.models.CharField(max_length=100, null=False, blank=False,validators=[validate_email,])
    city = django.db.models.ForeignKey(City, blank=True, null=True)
    roles = django.db.models.ManyToManyField(Role)
    user = django.db.models.ForeignKey(User)
    first_name = django.db.models.CharField(max_length=100, null=False, blank=False)
    last_name = django.db.models.CharField(max_length=100, null=True, blank=True)
    personal_title = django.db.models.CharField(max_length=5, null=True, blank=True)

    def has_role(self, role_name):
        ret = False
        for role in self.roles.all():  # everyone has at least one role
            if role.name == ROLES[role_name]:
                ret = True
                break
        return ret

    def is_focal_point(self):
        return self.has_role(ROLE_FOCAL_POINT_ITEM)

    def is_crpt_team(self):
        return self.has_role(ROLE_CRPT_TEAM_ITEM)


class Assessment(BasicName):
    """
    Represents an assessment uploaded by a focal point
    """
    def validate_size(file_field):
        file_size = file_field.file.size
        megabyte_limit = 2.0
        if file_size > megabyte_limit*1024*1024:
            raise ValidationError("Max file size is %sMB" % str(megabyte_limit))

    def validate_format(file_field):
        dot_position = file_field.name.find('.')
        if (dot_position == -1):
            raise ValidationError(u'File type not supported! ')

        ext = file_field.name[dot_position:len(file_field.name)]
        valid_extensions = ['.xlsx']

        if not ext in valid_extensions:
            raise ValidationError(u'File type not supported! ' + ext)

    file = django.db.models.FileField(null=False, blank=False, validators=[validate_size, validate_format],
                                      upload_to="./")
    date_uploaded = django.db.models.DateField(null=True, blank=True)
    version = django.db.models.CharField(max_length=10, null=True, blank=True)
    comments = django.db.models.TextField(null=True, blank=True)
    focal_point = django.db.models.ForeignKey(Person)
    city = django.db.models.ForeignKey(City)
    results_url = django.db.models.CharField(max_length=500, null=True, blank=True)

    def get_remote_folder(self):
        return self.city.name + "_" + str(self.date_uploaded)


class TraceAction(Common):
    """
    Represents an action traced by the system
    """
    action = django.db.models.CharField(max_length=50, null=False, blank=False)
    person = django.db.models.ForeignKey(Person)
    assessment = django.db.models.ForeignKey(Assessment, null=True, blank=True)
    date = django.db.models.DateTimeField(default=timezone.now, null=False, blank=False)