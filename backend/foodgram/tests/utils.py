from rest_framework import status
from rest_framework.test import APITestCase

from foodgram import models


class APIResponseTestCase(APITestCase):
    def assert_response(
        self, url, method='get', data=None,
        expected_status=status.HTTP_200_OK,
        expected_data=None,
        login_as=None,
    ):
        if login_as is not None:
            self.client.force_authenticate(login_as)
        func = getattr(self.client, method)
        if data is None:
            response = func(url)
        else:
            response = func(url, data)
        self.assertEqual(response.status_code, expected_status)
        if expected_data is not None:
            for k, v in expected_data.items():
                self.assertEqual(response.data.get(k), v)
        return response

    def assert_invalid_data(self, url, data, method='post', login_as=None):
        for key in data.keys():
            test_data = data.copy()
            test_data.pop(key)
            self.assert_response(
                url, method, test_data,
                status.HTTP_400_BAD_REQUEST,
                login_as=login_as)


def create_user(username):
    user = models.User(
        email=f'{username}@example.com',
        username=username,
        first_name='test',
        last_name='user',
        is_active=True
    )
    user.set_password('foodgram_test')
    user.save()
    return user


def get_user_json_short(id=None, username=None, user=None):
    if user is not None:
        id = user.pk
        username = user.username
    return {
        'id': id,
        'email': f'{username}@example.com',
        'username': username,
        'first_name': 'test',
        'last_name': 'user'
    }


def get_user_json(id=None, username=None, user=None, subscribed=False, avatar=''):
    res = get_user_json_short(id, username, user)
    res.update(
        is_subscribed=subscribed,
        avatar=avatar
    )
    return res
