# from __future__ import unicode_literals

import csv
import sys
import os


import datetime

from django.conf import settings

project_path = "/Users/miquel/UN/0003-CRPTDEV/CRPT201510/"
sys.path.append(project_path)
os.environ['DJANGO_SETTINGS_MODULE'] = 'crpt201510.settings'


# OBS: to initialize Django in 1.7 and run python scripts. Do not include 'setup' in installed_apps
import django
django.setup()

from django.contrib.auth.models import User, Group
from crpt201510.models import *

def load_users_file():
    """
    Load into database users for cities in users.csv file
    :return:
    """
    print("load_users_file. Start..")
    file_path = settings.BASE_DIR + "/files/users.tsv"
    data_reader = csv.reader(open(file_path), dialect='excel-tab')
    data_reader.next()  # to skip headers row
    for row in data_reader:
        # read data from line
        username = row[0].strip()
        pwd = row[1].strip()
        email = row[2].strip()
        group_name = row[3].strip()
        first_name = row[4].strip()
        last_name = row[5].strip()
        # check before creation
        try:
            user = User.objects.get(username=username)
            print("User yet exists: " + row[0].strip())
        except:
            print("User does not exist: " + row[0].strip())
            user = User.objects.create_user(username, email, pwd)
        # create/update  user and eventually new group
        try:
            group = get_user_group(group_name)

            user.first_name = first_name
            user.last_name = last_name
            user.save()
            user.groups.add(group)
        except:
            print("Error creating user: " + username)
            print("Unexpected error:", sys.exc_info())
    print("load_users_file. End....")


def get_user_group(group_name):
    """
    gets or create a user group
    :param group_name:
    :return:
    """
    try:
        group = Group.objects.get(name=group_name)
        return group
    except:
        print("Group does not exist: " + group_name)
        try:
            group = Group()
            group.name = group_name
            group.save()
            print("Group created: " + group_name)
            return group
        except:
            print("Error creating group: " + group_name)


def load_entity_single_field_name(file_name, class_name):
    """
    Load file of entities with a single field name
    :param file_name:
    :param class_name:
    :return:
    """
    print("load_entity_single_field_name: " + file_name + " .Start...")
    file_path = settings.BASE_DIR + "/files/" + file_name
    data_reader = csv.reader(open(file_path), dialect='excel-tab')
    for row in data_reader:
        entity = class_name()
        entity.name = row[0].strip()
        try:
            entity.save()
        except:
            print("Unexpected error:", sys.exc_info())
    print("load_entity_single_field_name: " + file_name + " .End.")


def load_people():
    """
    Load persons file
    :return:
    """
    print("load_people. Start...")
    file_path = settings.BASE_DIR + "/files/" + "people.tsv"
    data_reader = csv.reader(open(file_path), dialect='excel-tab')
    data_reader.next()  # to skip headers row
    for row in data_reader:
        # check if user exists. if not trace and skip row
        try:
            try:
                user = User.objects.get(username=row[4].strip())
                print("username: " + row[4].strip())
            except:
                print("User does not exist: " + row[6].strip())
                print("Unexpected error:", sys.exc_info())

            # check if person exists to update it. If not, create it
            try:
                person = Person.objects.get(user=user)
                print("Person exists: " + person.name)
            except:
                print("Person does not exist: " + user.username)
                person = Person()
            person.title = row[0].strip()
            person.phone_no = row[1].strip()
            person.email = row[2].strip()
            try:
              person.city = City.objects.get(name=row[3].strip())
            except:
                print("City does not exist: " + row[3].strip())
            person.personal_title = row[5].strip()
            person.first_name = row[6].strip()
            person.last_name = row[7].strip()
            person.name = person.last_name + ", " + person.first_name
            # update user
            person.user = user
            person.save()
            # update roles
            for i in range(8,10):
                try:
                    person.roles.add(Role.objects.get(name=row[i].strip()))
                    person.save()
                except:
                    pass
        except:
            print("Unexpected error:", sys.exc_info())
    print("load_people. End.")





if __name__ == "__main__":
    load_entity_single_field_name("cities.tsv", City)
    load_entity_single_field_name("roles.tsv", Role)
    load_users_file()
    load_people()






