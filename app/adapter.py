# app/adapter.py

from allauth.socialaccount.adapter import DefaultSocialAccountAdapter

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def get_login_redirect_url(self, request, socialaccount):
        # Customize the redirect URL here to go directly to the Google account selection page
        return '/accounts/google/login/?auth_params=' + socialaccount.socialtoken_set.first().token
