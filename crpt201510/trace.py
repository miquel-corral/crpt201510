import sys
from django.core import serializers

from crpt201510.models import TraceAction

def trace_action(action_name, person, assessment=None):
    try:
        new_log = TraceAction()
        new_log.action = action_name
        new_log.person = person
        new_log.assessment = assessment
        new_log.save()
    except:
        print("Error tracing action: " + action_name)
        print("Error: " + str(sys.exc_info()))

