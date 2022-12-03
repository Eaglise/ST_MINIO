from django.shortcuts import render, redirect
import django.conf as conf
from MINIO.models import Document, MyDocument
from MINIO.forms import DocumentForm, MyDocumentForm
from minio import Minio
import os
import time
import glob
from django.http import JsonResponse, HttpResponse
import json
import ast
import datetime
import pytz
from django.conf import settings


GlobalData = {
    'last_date': 0
}
GD=0

def global_data_update(request):
  global GD
  newdata=request.POST.get('date')
  body=str(request.body)
  body=(body.replace(' ', ''))[2:-1]
  rawdate=int(body)
  GD=rawdate

  return JsonResponse({})


def start(request):
  return render(request, 'start.html')


def home(request):
  clean_static()
  if request.method == 'POST':
    request.session['access'] = request.POST['access']
    request.session['secret'] = request.POST['secret']
  access = request.session.get('access')
  conf.settings.AWS_STORAGE_BUCKET_NAME = access
  client = Minio(endpoint="localhost:9000", access_key=access, secret_key=request.session.get('secret'), secure=False)

  objects = client.list_objects(access)

  return render(request, 'home.html', {'objects': objects})


def object(request, name):

  access = request.session.get('access')
  client = Minio(endpoint="localhost:9000", access_key=access, secret_key=request.session.get('secret'), secure=False)

  filename = name
  filepath = "MINIO/static/video/" + filename
  getobject = client.fget_object(access, filename, filepath)

  object_info = client.stat_object(access, name)

  if request.method == 'POST':
    client.remove_object(access, name)
    return redirect('deleted')

  return render(request, 'object.html', {'object_name': name, 'object_info': object_info, 'client': client, 'access': access})


def model_form_upload(request):
  clean_static()
  if request.method == 'POST':
    form = MyDocumentForm(request.POST, request.FILES)
    if form.is_valid():
      newdoc = MyDocument(doc=request.FILES['doc'])
      newdoc.save()

      for filename, file in request.FILES.items():
        name = request.FILES[filename].name
      request.session['filename'] = name

      access = request.session.get('access')
      client = Minio(endpoint="localhost:9000", access_key=access, secret_key=request.session.get('secret'), secure=False)
      filepath = "MINIO/static/video/" + name

      client.fput_object(access, name, filepath)

      return redirect('home')
  else:
    form = MyDocumentForm()

  return render(request, 'model_form_upload.html', {'form': form},)


def model_form_edit(request, name):
  clean_static()
  if request.method == 'POST':
    global GD
    form = MyDocumentForm(request.POST, request.FILES)

    if (request.FILES):
      newdoc = MyDocument(doc=request.FILES['fileList'])
      newdoc.save()
      for filename, file in request.FILES.items():
        fname = request.FILES[filename].name
      # request.session['filename'] = fname

      access = request.session.get('access')
      client = Minio(endpoint="localhost:9000", access_key=access, secret_key=request.session.get('secret'), secure=False)
      filepath = "MINIO/static/video/" + fname

      object_info = client.stat_object(access, name)
      utc = pytz.UTC
      last_date_modified = object_info.last_modified
      new_date_modified = utc.localize(datetime.datetime.fromtimestamp(GD / 1e3))

      if (last_date_modified < new_date_modified):
        client.fput_object(access, name, filepath)
        return redirect('home')
      else:
        return redirect('sync_error', name)

    if form.is_valid():
      newdoc = MyDocument(doc=request.FILES['doc'])
      newdoc.save()

      access = request.session.get('access')
      client = Minio(endpoint="localhost:9000", access_key=access, secret_key=request.session.get('secret'), secure=False)
      for filename, file in request.FILES.items():
        fname = request.FILES[filename].name
      filepath = "MINIO/static/video/" + fname

      client.fput_object(access, name, filepath)

      return redirect('home')
  else:
    form = MyDocumentForm()

  return render(request, 'model_form_edit.html', {'form': form, 'name': name}, )


def deleted(request, name):
  access = request.session.get('access')
  client = Minio(endpoint="localhost:9000", access_key=access, secret_key=request.session.get('secret'), secure=False)

  if request.method == 'POST':
    client.remove_object(access, request.POST['delete_object'])

  return render(request, 'deleted.html', {'name': name})


def sync_error(request, name):
  return render(request, 'sync_error.html', {'name': name})


def clean_static():
  files = glob.glob('MINIO/static/video/*')
  for f in files:
    os.remove(f)
  return


def download(request, file_name):
  file_path = settings.MEDIA_ROOT + '/' + file_name
  response = HttpResponse(open(file_path, 'rb').read())
  response['X-Sendfile'] = file_path
  response['Content-Length'] = os.stat(file_path).st_size
  response['Content-Disposition'] = 'attachment; filename='+file_name
  response['Content-Type'] = 'video/mp4'

  return response
