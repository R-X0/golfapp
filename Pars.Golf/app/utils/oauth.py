from flask import url_for, current_app, redirect, request, session
import json
from rauth import OAuth1Service, OAuth2Service
from urllib.parse import urlencode
import urllib.request

class OAuthSignIn:
    providers = None
    
    def __init__(self, provider_name):
        self.provider_name = provider_name
        credentials = current_app.config['OAUTH_CREDENTIALS'][provider_name]
        self.consumer_id = credentials['id']
        self.consumer_secret = credentials['secret']
        
    def authorize(self):
        pass
        
    def callback(self):
        pass
        
    def get_callback_url(self):
        return url_for('auth.oauth_callback', provider=self.provider_name, _external=True)
        
    @classmethod
    def get_provider(cls, provider_name):
        if cls.providers is None:
            cls.providers = {}
            for provider_class in cls.__subclasses__():
                provider = provider_class()
                cls.providers[provider.provider_name] = provider
        return cls.providers.get(provider_name)
        
class GoogleSignIn(OAuthSignIn):
    def __init__(self):
        super(GoogleSignIn, self).__init__('google')
        self.service = OAuth2Service(
            name='google',
            client_id=self.consumer_id,
            client_secret=self.consumer_secret,
            authorize_url='https://accounts.google.com/o/oauth2/auth',
            access_token_url='https://accounts.google.com/o/oauth2/token',
            base_url='https://www.googleapis.com/oauth2/v1/'
        )
        
    def authorize(self):
        return redirect(self.service.get_authorize_url(
            scope='email',
            response_type='code',
            redirect_uri=self.get_callback_url())
        )
        
    def callback(self):
        if 'code' not in request.args:
            return None, None, None
        
        oauth_session = self.service.get_auth_session(
            data={'code': request.args['code'],
                  'grant_type': 'authorization_code',
                  'redirect_uri': self.get_callback_url()},
            decoder=json.loads
        )
        me = oauth_session.get('userinfo').json()
        
        # Google specific handling
        return (
            me['id'],
            me.get('email'),
            me.get('name')
        )
        
class TwitterSignIn(OAuthSignIn):
    def __init__(self):
        super(TwitterSignIn, self).__init__('twitter')
        self.service = OAuth1Service(
            name='twitter',
            consumer_key=self.consumer_id,
            consumer_secret=self.consumer_secret,
            request_token_url='https://api.twitter.com/oauth/request_token',
            authorize_url='https://api.twitter.com/oauth/authorize',
            access_token_url='https://api.twitter.com/oauth/access_token',
            base_url='https://api.twitter.com/1.1/'
        )
        
    def authorize(self):
        try:
            request_token = self.service.get_request_token(
                params={'oauth_callback': self.get_callback_url()}
            )
            session['request_token'] = request_token
            return redirect(self.service.get_authorize_url(request_token[0]))
        except Exception as e:
            print(f"Error in Twitter authorize: {str(e)}")
            return redirect(url_for('main.index'))
        
    def callback(self):
        # Note: Twitter OAuth1 requires session handling
        if 'request_token' not in session:
            return None, None, None
            
        try:
            request_token = session.pop('request_token')
            
            if 'oauth_verifier' not in request.args:
                return None, None, None
                
            oauth_session = self.service.get_auth_session(
                request_token[0],
                request_token[1],
                data={'oauth_verifier': request.args['oauth_verifier']}
            )
                
            me = oauth_session.get('account/verify_credentials.json').json()
            
            # Twitter doesn't provide email by default
            return (
                me['id_str'],
                None,  # Email not provided by Twitter
                me['screen_name']
            )
        except Exception as e:
            print(f"Error in Twitter callback: {str(e)}")
            return None, None, None