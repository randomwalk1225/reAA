"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.http import HttpResponse
from django.contrib.auth import get_user_model

# 임시 비밀번호 재설정 (사용 후 삭제할 것)
def temp_reset_password(request):
    secret = request.GET.get('secret')
    if secret != 'hydrolink2024reset':
        return HttpResponse('Forbidden', status=403)

    email = request.GET.get('email')
    new_password = request.GET.get('pw')

    if not email or not new_password:
        User = get_user_model()
        users = User.objects.all()
        user_list = '<br>'.join([f'{u.username} | {u.email} | superuser: {u.is_superuser}' for u in users])
        return HttpResponse(f'<pre>Users:\n{user_list}\n\nUsage: ?secret=hydrolink2024reset&email=xxx&pw=newpassword</pre>')

    User = get_user_model()
    user = User.objects.filter(email=email).first()
    if user:
        user.set_password(new_password)
        user.save()
        return HttpResponse(f'Password updated for {email}')
    return HttpResponse(f'User not found: {email}', status=404)

urlpatterns = [
    path('_temp_reset/', temp_reset_password),  # 임시 - 사용 후 삭제
    path('admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('measurement/', include('measurement.urls')),
    path('satellite/', include('satellite.urls')),
    path('hydro/', include('hydro.urls')),
    # Authentication
    path('accounts/', include('allauth.urls')),
]
