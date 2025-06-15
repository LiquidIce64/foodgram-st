from rest_framework import status
from rest_framework.test import APITestCase

from foodgram import models


class APIResponseTestCase(APITestCase):
    def assert_response(
        self, url, method='get', data=None,
        expected_status=status.HTTP_200_OK,
        expected_data=None
    ):
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


def create_user(username):
    return models.User.objects.create(
        email=f'{username}@example.com',
        username=username,
        first_name='test',
        last_name='user',
        password='foodgram_test'
    )


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
