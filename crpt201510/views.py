import sys
import time

from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import ensure_csrf_cookie
from django.core.paginator import Paginator
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect, render_to_response
from django.template.response import TemplateResponse
from django.http import HttpResponse
from django.template import RequestContext, loader, Context
from django.forms.models import modelformset_factory
import datetime



from crpt201510.constants import *
from crpt201510.business_utils import *
from crpt201510.env_utils import *
from crpt201510.models import Assessment
from crpt201510.trace import *
from crpt201510.ftp_utils import *



@ensure_csrf_cookie
def my_login(request):
    username = ''
    password = ''
    user = None

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(username=username, password=password)

            if user is not None:
                if user.is_active:
                    login_response = login(request, user)
                    request.session['username'] = username
                    # control if UN-Habitat or expert staff
                    person = get_person_by_user(user)
                    if person.has_role(ROLE_CRPT_TEAM_ITEM):
                        # TODO: set web section for crpt team
                        return redirect('/crpt_team/')
                    else:
                        trace_action(TRACE_LOGIN, person)
                        return redirect('/index/')
                else:
                    # Return a 'disabled account' error message
                    context = {'form': form}
                    return redirect('/login/?next=%s' % request.path)
            else:
                # Return an 'invalid login' error message.
                context = {'form': form}
                return TemplateResponse(request, 'crpt201510/login.html', context)
        else:
            context = {'form': form}
            return TemplateResponse(request, 'crpt201510/login.html', context)
    else:
        form = AuthenticationForm(request)
        context = {'form': form,
                   'is_login': 'is_login',
            }
        return TemplateResponse(request, 'crpt201510/login.html', context)

@ensure_csrf_cookie
def my_logout(request):
    person = get_person(request)
    logout(request)
    trace_action(TRACE_LOGOUT, person)
    template = loader.get_template('crpt201510/logout.html')
    context = RequestContext(request, {'is_logout': "logout"})
    return HttpResponse(template.render(context))

@ensure_csrf_cookie
def my_change_password(request):
    try:
        if request.method == 'POST':
            form = PasswordChangeForm(data=request.POST, user=request.user)
            if form.is_valid():
                # change password
                #raise Exception("EL USUARIO: " + request.user.username)
                #raise Exception("EL pwd: " + str(request.POST['new_password1']).strip())
                u = User.objects.get(username=request.user.username)
                u.set_password(str(request.POST['new_password1']).strip())
                u.save()
                # logout
                logout(request)
                # return to index page
                return redirect('/index/')
            else:
                context = {'form': form, 'is_login':'is_login'}
                return TemplateResponse(request, 'crpt201510/change_password.html', context)
        else:
            form = PasswordChangeForm(request)
            context = {'form': form,
                       'is_login':'is_login',
                }
            return TemplateResponse(request, 'crpt201510/change_password.html', context)
    except:
        if debug_is_on():
            raise
        else:
            return redirect("/index/", context_instance=RequestContext(request))

@ensure_csrf_cookie
@login_required
def index(request):
    """
    View for the list of sections of the index card

    :param request:
    :return:
    """
    try:
        assessment_list = None
        assessments_paginated = None
        user = None
        person = None

        # get username from session
        username = request.session.get('username')
        person = get_person_by_username(username)

        if not username or not person:
            return redirect('my_login')
        try:
            # assessments for the city of the user
            assessment_list = Assessment.objects.filter(city=person.city)

        except:
            raise Exception(sys.exc_info())

        paginator = Paginator(assessment_list, ITEMS_PER_PAGE)  # Limit items per page
        page = request.GET.get('page')
        try:
            assessments_paginated = paginator.page(page)
        except:
            #print("Unexpected error:", sys.exc_info())
            assessments_paginated = paginator.page(1)

        template = loader.get_template('crpt201510/index.html')
        context = RequestContext(request, {
            'assessments_list': assessments_paginated,
            'username': username,
            'user': user,
            'person': person,
        })
        return HttpResponse(template.render(context))
    except:
        if debug_is_on():
            raise
        else:
            return render_to_response("crpt201510/error.html",
                                      {"error_description": sys.exc_info(),},
                                      context_instance=RequestContext(request))


def my_copyright(request):
    """
    View for the my_copyright page

    :param request:
    :return:
    """
    username = request.session.get('username')
    try:
        index_card = None
        #index_card = IndexCard.objects.get(username=username)
    except:
        index_card = None
    template = loader.get_template('crpt201510/copyright.html')
    context = RequestContext(request, {
        'username': username,
        'is_copyright': 'is_copyright',
    })
    return HttpResponse(template.render(context))


@ensure_csrf_cookie
@login_required
def retrieve_file(request, remote_folder, remote_file):
    """
    retrieve_file
    :param request:
    :param expert_request_id:
    :return:
    """
    try:
        # check ftp
        if ftp_is_off():
            return render_to_response("crpt201510/error.html",
                                      {"error_description": "Service temporary unavailable.",},
                                      context_instance=RequestContext(request))
        # get the file
        file_content = get_ftp_file_content(remote_folder, remote_file)
        if file_content is None:
            raise Exception("file_content is null!!")
        else:
            # return the file
            content_type = "application"
            extension = remote_file[-3:len(remote_file)]

            if extension == "xls":
                content_type = "application/vnd.ms-excel"
            if extension == "lsx":
                content_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            if extension == "pdf":
                content_type = "application/pdf"

            response = HttpResponse(file_content, content_type=content_type)
            response['Content-Disposition'] = 'inline;filename=' + remote_file
            return response
    except:
        if debug_is_on():
            raise
        else:
            return render_to_response("crpt201510/error.html",
                                      {"error_description": sys.exc_info(),},
                                      context_instance=RequestContext(request))


@ensure_csrf_cookie
@login_required
def upload_assessment(request):
    """
    View for the upload assessment page
    :param request:
    :param request_id:
    :return:
    """
    try:
        person = get_person(request)
        query_set = None
        assessment_form_set = modelformset_factory(Assessment, max_num=1, exclude=[])

        if request.method == 'POST':
            formset = assessment_form_set(request.POST, request.FILES)


            if formset.is_valid():
                # get instance
                assessment = formset[0].save(commit=False)

                # set date uploaded
                assessment.date_uploaded = datetime.datetime.date(datetime.datetime.now())

                # save assessment
                assessment.save()

                # upload file to ftp.
                upload_file(assessment.get_remote_folder(), str(assessment.file))

                # trace action
                trace_action(TRACE_UPLOAD_ASSESSMENT, person, assessment)

                return redirect("/index/", context_instance=RequestContext(request))
            else:
                if format(len(formset.errors) > 0):
                    num_errors = len(formset.errors[0])
        else:
            query_set = Assessment.objects.filter(pk=None)
            formset = assessment_form_set(queryset=query_set)

        # initial values
        if not query_set:
            # upload date
            formset[0].fields['date_uploaded'].initial = time.strftime("%Y%m%d")
            # city
            formset[0].fields['city'].initial = person.city.id
            # person
            formset[0].fields['focal_point'].initial = person.id

        return render_to_response("crpt201510/upload_assessment.html",
                                  {"formset": formset, "person": person,
                                   "is_logout":"is_logout"},
                                  context_instance=RequestContext(request))
    except:
        if debug_is_on():
            raise
        else:
            return render_to_response("crpt201510/error.html",
                                      {"error_description": sys.exc_info(),},
                                      context_instance=RequestContext(request))


@ensure_csrf_cookie
@login_required
def graphics(request, assessment_id):
    try:
        assessment = Assessment.objects.get(id=assessment_id)

        template = loader.get_template('crpt201510/graphics.html')
        context = RequestContext(request, {'is_logout': "logout", 'assessment': assessment,})

        return HttpResponse(template.render(context))
    except:
        if debug_is_on():
            raise
        else:
            return render_to_response("crpt201510/error.html",
                                      {"error_description": sys.exc_info(),},
                                      context_instance=RequestContext(request))