from .utils import (
    APIResponseTestCase, status, TEST_IMAGE_DATA,
    create_user, get_user_json
)
from . import structs


def get_user_url(user_id):
    return f'/api/users/{user_id}/'


URL_USERS = '/api/users/'
URL_PROFILE = '/api/users/me/'
URL_AVATAR = '/api/users/me/avatar/'
URL_PASSWORD = '/api/users/set_password/'
URL_LOGIN = '/api/auth/token/login/'
URL_LOGOUT = '/api/auth/token/logout/'

USER_CREATE_DATA = {
    'email': f'test_user4@example.com',
    'username': 'test_user_4',
    'first_name': 'test',
    'last_name': 'user',
    'password': 'foodgram_test'
}

AVATAR_CREATE_DATA = {
    'avatar': TEST_IMAGE_DATA
}


class UserTestCase(APIResponseTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user1 = create_user('test_user_1')
        cls.user2 = create_user('test_user_2')
        cls.user3 = create_user('test_user_3')

    def test_list(self):
        self.assert_response(
            URL_USERS,
            expected_data={
                'results': [
                    get_user_json(user=self.user1),
                    get_user_json(user=self.user2),
                    get_user_json(user=self.user3)
                ]
            })

    def test_detail(self):
        self.assert_response(
            get_user_url(self.user1.pk),
            expected_data=get_user_json(user=self.user1))
        self.assert_response(
            get_user_url(self.user2.pk),
            expected_data=get_user_json(user=self.user2))
        self.assert_response(
            get_user_url(self.user3.pk),
            expected_data=get_user_json(user=self.user3))

    def test_detail_not_found(self):
        self.assert_response(
            get_user_url(99999999),
            expected_status=status.HTTP_404_NOT_FOUND)

    def test_create(self):
        self.assert_response(
            URL_USERS, method='post',
            data=USER_CREATE_DATA,
            expected_status=status.HTTP_201_CREATED,
            expected_struct=structs.user_short)

    def test_create_invalid(self):
        self.assert_invalid_data(URL_USERS, USER_CREATE_DATA)

    def test_profile(self):
        self.assert_response(
            URL_PROFILE,
            login_as=self.user1,
            expected_data=get_user_json(user=self.user1))

    def test_profile_no_auth(self):
        self.assert_response(
            URL_PROFILE,
            expected_status=status.HTTP_401_UNAUTHORIZED)

    def test_avatar(self):
        response = self.assert_response(
            URL_AVATAR, method='put',
            login_as=self.user1,
            data=AVATAR_CREATE_DATA)
        self.assertRegex(response.data.get('avatar'), r'https?:\/\/[^\/]+\/media\/users\/.*\..*')

    def test_avatar_invalid(self):
        self.assert_response(
            URL_AVATAR, method='put',
            login_as=self.user1,
            data={},
            expected_status=status.HTTP_400_BAD_REQUEST)

    def test_avatar_delete(self):
        self.assert_response(
            URL_AVATAR, method='delete',
            login_as=self.user1,
            expected_status=status.HTTP_204_NO_CONTENT)

    def test_avatar_no_auth(self):
        self.assert_response(
            URL_AVATAR, method='put',
            expected_status=status.HTTP_401_UNAUTHORIZED)
        self.assert_response(
            URL_AVATAR, method='delete',
            expected_status=status.HTTP_401_UNAUTHORIZED)

    def test_password(self):
        self.assert_response(
            URL_PASSWORD, method='post',
            login_as=self.user1,
            data={
                'new_password': 'foodgram_test2',
                'current_password': 'foodgram_test'
            },
            expected_status=status.HTTP_204_NO_CONTENT)

    def test_password_invalid(self):
        self.assert_invalid_data(
            URL_PASSWORD,
            login_as=self.user1,
            data={
                'new_password': 'foodgram_test2',
                'current_password': 'foodgram_test'
            })

    def test_password_no_auth(self):
        self.assert_response(
            URL_PASSWORD, method='post',
            expected_status=status.HTTP_401_UNAUTHORIZED)

    def test_login(self):
        response = self.assert_response(
            URL_LOGIN, method='post',
            data={
                'email': 'test_user_1@example.com',
                'password': 'foodgram_test'
            })
        self.assertIsNotNone(response.data.get('auth_token', None))

    def test_logout(self):
        self.assert_response(
            URL_LOGOUT, method='post',
            login_as=self.user1,
            expected_status=status.HTTP_204_NO_CONTENT)

    def test_logout_no_auth(self):
        self.assert_response(
            URL_LOGOUT, method='post',
            expected_status=status.HTTP_401_UNAUTHORIZED)
