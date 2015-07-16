from django.db import models
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.file import Storage
from oauth2client.django_orm import FlowField
from oauth2client.django_orm import CredentialsField
from django.http import HttpRequest
import urllib
import urllib2
import os
import logging
from httplib2 import Http
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.http import HttpResponseBadRequest
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from oauth2client import xsrfutil
from oauth2client.client import flow_from_clientsecrets
from oauth2client.django_orm import Storage
from django.conf import settings
from django.contrib.auth.models import User
import random
from django.shortcuts import redirect


class CredentialsModel(models.Model):
    id = models.ForeignKey(User, primary_key=True)
    credential = CredentialsField()

class SendData(models.Model):
    name = models.CharField(max_length=200, blank=False)
    email = models.CharField(max_length=200, blank=False)
    store_id=models.PositiveSmallIntegerField(blank=True)

    def authorize(self, request, scope_url):
        scope = scope_url
        # session = request.session
        if(self.store_id==False):
            self.store_id = random.seed()
        session=self.store_id
        
        CLIENT_SECRETS = os.path.join(
            os.path.dirname(__file__), 'secrets.json')
        flow = flow_from_clientsecrets(CLIENT_SECRETS,
                           scope=scope,
                           redirect_uri='http://localhost:8000/admin')
        # credential = CredentialsModel()
        # if session == False:
        #     flow.params['state'] = xsrfutil.generate_token(settings.SECRET_KEY,
        #                                                    session)
        #     authorize_url = flow.step1_get_authorize_url()
        #     authorize_url = HttpResponseRedirect(authorize_url)
        #     credential = flow.step2_exchange(authorize_url)
        #     storage = Storage(CredentialsModel, 'id', session, 'credential')
        #     storage.put(credential)
        # else:0
        #     storage = Storage(CredentialsModel, 'id', session, 'credential')
        #     credential = storage.get()
        #
        #     if credential is None or credential.invalid == True:
        #         flow.params['state'] = xsrfutil.generate_token(settings.SECRET_KEY,
        #                                                        session)
        #         authorize_url = flow.step1_get_authorize_url()
        #         authorize_url = HttpResponseRedirect(authorize_url)
        #         credential = flow.step2_exchange(authorize_url)
        #         storage = Storage(CredentialsModel, 'id', session, 'credential')
        #         storage.put(credential)
        storage = Storage(CredentialsModel, 'id', session, 'credential')
        credential = storage.get()
        if credential is None or credential.invalid == True:
            flow.params['state'] = xsrfutil.generate_token(settings.SECRET_KEY,
                                                           session)
            authorize_url = flow.step1_get_authorize_url()
            authorize_url = redirect(authorize_url)
            credential = flow.step2_exchange(authorize_url)
            storage = Storage(CredentialsModel, 'id', session, 'credential')
            storage.put(credential)
        credential = flow.step2_exchange(credential)
        return credential

    def make_mailing_list(self, request):
        name = self.name
        email = self.email
        final = "https://www.googleapis.com/admin/directory/v1/groups"
        scope = "https://www.googleapis.com/auth/admin.directory.group"
        post_data = {
            "email": email,
            "name": name
        }
        credential= self.authorize(HttpRequest ,scope)
        the_page = credential.authorize(request.POST(final, post_data))
        # post_data=urllib.urlencode(post_data)
        # result = credential.authorize(urllib2.Request(final, post_data))
        # response = urllib2.urlopen(result)
        # the_page = response.read()
        return the_page


class MailingList(models.Model):
    name = models.CharField(max_length=200, blank=False)
    email = models.CharField(max_length=200, blank=False)

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        sending = SendData()
        sending.name=self.name
        sending.email = self.email
        response = HttpRequest()
        sending.make_mailing_list(response)
        return super(MailingList, self).save(*args, **kwargs)



class Staff(models.Model):
    first_name = models.CharField(max_length=200, blank=False)
    last_name = models.CharField(max_length=200, blank=False)
    email = models.CharField(max_length=200, blank=False, default='')
    position = models.CharField(max_length=200, blank=True)
    department = models.CharField(max_length=200, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    picture = models.ImageField(blank=True)
    mailing_lists = models.ManyToManyField(MailingList)