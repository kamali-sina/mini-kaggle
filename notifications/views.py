from django.template.loader import render_to_string
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render

from notifications.models import NotificationSource
from notifications.forms import CreateNotificationSourceForm, NOTIFICATION_TYPED_FORM_REGISTRY


# Create your views here.

@login_required
def create_notification_source(request):
    if request.method == 'POST':
        form = CreateNotificationSourceForm(request.POST, user=request.user)
        typed_form = NOTIFICATION_TYPED_FORM_REGISTRY[request.POST['type']](request.POST)
        if form.is_valid():
            form.save()
            if 'next' in request.POST:
                return HttpResponseRedirect(request.POST['next'])
            messages.success(request, "Notification source created successfully :)")
    else:
        form = CreateNotificationSourceForm(user=request.user)
        typed_form = NOTIFICATION_TYPED_FORM_REGISTRY[NotificationSource.DEFAULT_TYPE]()
    context = {'form': form,
               'typed_form': typed_form,
               'next': request.GET.get('next', '')}
    return HttpResponse(
        render(request, 'notifications/create_notification.html', context=context))


def get_typed_notification_form(request, notification_type):
    context = {'form': NOTIFICATION_TYPED_FORM_REGISTRY[notification_type]()}
    return JsonResponse({'form': render_to_string('registration/base_inline_form.html', context=context)})
