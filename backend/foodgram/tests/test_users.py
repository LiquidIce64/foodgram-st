from .utils import APIResponseTestCase, status, create_user, get_user_json


def get_detail_url(user_id):
    return f'/api/users/{user_id}/'


URL_USERS = '/api/users/'
URL_PROFILE = '/api/users/me/'
URL_AVATAR = '/api/users/me/avatar/'
URL_PASSWORD = '/api/users/set_password/'
URL_LOGIN = '/api/auth/token/login/'
URL_LOGOUT = '/api/auth/token/logout/'

USER_STRUCT = {
    'id': int,
    'username': str,
    'email': str,
    'first_name': str,
    'last_name': str
}

USER_CREATE_DATA = {
    'email': f'test_user4@example.com',
    'username': 'test_user_4',
    'first_name': 'test',
    'last_name': 'user',
    'password': 'foodgram_test'
}

AVATAR_CREATE_DATA = {
    'avatar': 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAA\
AEAAAABAgMAAABieywaAAAACVBMVEUAAAD///9fX1/S0ecCAAAACXBIWXMAAA7\
EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOyYQAAAABJRU5ErkJggg=='
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
            get_detail_url(self.user1.pk),
            expected_data=get_user_json(user=self.user1))
        self.assert_response(
            get_detail_url(self.user2.pk),
            expected_data=get_user_json(user=self.user2))
        self.assert_response(
            get_detail_url(self.user3.pk),
            expected_data=get_user_json(user=self.user3))

    def test_detail_not_found(self):
        self.assert_response(
            get_detail_url(99999999),
            expected_status=status.HTTP_404_NOT_FOUND)

    def test_create(self):
        response = self.assert_response(
            URL_USERS, method='post',
            data=USER_CREATE_DATA,
            expected_status=status.HTTP_201_CREATED)
        self.assert_json_structure(response.data, USER_STRUCT)

    def test_create_invalid(self):
        self.assert_invalid_data(URL_USERS, USER_CREATE_DATA)

    def test_profile(self):
        self.assert_response(
            URL_PROFILE,
            expected_data=get_user_json(user=self.user1),
            login_as=self.user1)

    def test_profile_no_auth(self):
        self.assert_response(
            URL_PROFILE,
            expected_status=status.HTTP_401_UNAUTHORIZED)

    def test_avatar(self):
        response = self.assert_response(
            URL_AVATAR, method='put',
            data=AVATAR_CREATE_DATA,
            login_as=self.user1)
        self.assertRegex(response.data.get('avatar'), r'https?:\/\/[^\/]+\/media\/users\/.*\..*')

    def test_avatar_invalid(self):
        self.assert_response(
            URL_AVATAR, method='put',
            data={},
            expected_status=status.HTTP_400_BAD_REQUEST,
            login_as=self.user1)

    def test_avatar_delete(self):
        self.assert_response(
            URL_AVATAR, method='delete',
            expected_status=status.HTTP_204_NO_CONTENT,
            login_as=self.user1
        )

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
            data={
                'new_password': 'foodgram_test2',
                'current_password': 'foodgram_test'
            },
            expected_status=status.HTTP_204_NO_CONTENT,
            login_as=self.user1)

    def test_password_invalid(self):
        self.assert_invalid_data(
            URL_PASSWORD,
            data={
                'new_password': 'foodgram_test2',
                'current_password': 'foodgram_test'
            },
            login_as=self.user1)

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
            expected_status=status.HTTP_204_NO_CONTENT,
            login_as=self.user1)

    def test_logout_no_auth(self):
        self.assert_response(
            URL_LOGOUT, method='post',
            expected_status=status.HTTP_401_UNAUTHORIZED)
