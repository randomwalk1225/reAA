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
    create = request.GET.get('create')

    User = get_user_model()

    # 사용자 생성
    if create and email and new_password:
        if User.objects.filter(email=email).exists():
            return HttpResponse(f'User already exists: {email}', status=400)
        user = User.objects.create_superuser(
            username=email.split('@')[0],
            email=email,
            password=new_password
        )
        return HttpResponse(f'Superuser created: {user.username} ({email})')

    # 비밀번호 변경
    if email and new_password:
        user = User.objects.filter(email=email).first()
        if user:
            user.set_password(new_password)
            user.save()
            return HttpResponse(f'Password updated for {email}')
        return HttpResponse(f'User not found: {email}', status=404)

    # 사용자 목록
    users = User.objects.all()
    user_list = '<br>'.join([f'{u.username} | {u.email} | superuser: {u.is_superuser}' for u in users]) or '(no users)'
    return HttpResponse(f'''<pre>Users:
{user_list}

Create superuser: ?secret=hydrolink2024reset&create=1&email=xxx&pw=password
Reset password: ?secret=hydrolink2024reset&email=xxx&pw=newpassword</pre>''')

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
