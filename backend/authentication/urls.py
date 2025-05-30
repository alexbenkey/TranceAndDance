from django.urls import path, include
from django.urls import re_path
from django.http import HttpResponse
from rest_framework_simplejwt.views import TokenRefreshView
from .views import RegisterView, LoginView, RefreshTokenView, google_callback,  login_42_redirect, login_42_callback, me, google_login, register_2fa ,disable_2fa, enable_2fa, login_2fa_required, sign_out, protected_user_data, DeleteAccountView
from django.http import JsonResponse

urlpatterns = [
	path('sign_out/', sign_out, name= 'sign_out'),
	path('login/', LoginView.as_view(), name='login'),
	path('register/', RegisterView.as_view(), name='register'),
    path('refresh/', RefreshTokenView.as_view(), name='token_refresh'),
    path('delete/', DeleteAccountView.as_view(), name='delete_account'),
    path('login-2fa/', login_2fa_required, name="login_2fa_required"),
    path('enable-2fa/', enable_2fa, name="enable_2fa"),
    path('register-2fa/', register_2fa, name="register_2FA"),
    path('disable-2fa/', disable_2fa, name ="disable_2fa"),
    path("google-login/", google_login, name="google_login"),
    path("google/callback/", google_callback, name="google_callback"),
    path('me/', me, name="me"),
    path("42/login/", login_42_redirect, name="login_42"),
    path("42/callback/", login_42_callback, name="callback_42"),
    path('ping/', lambda request: JsonResponse({"status": "ok"})),
    path('data/', protected_user_data, name="user_data"),
    re_path(r'^\.well-known/appspecific/com\.chrome\.devtools\.json$', lambda r: HttpResponse('', status=204)),

]