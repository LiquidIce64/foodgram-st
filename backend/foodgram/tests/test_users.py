from .utils import APIResponseTestCase, status, create_user, get_user_json


class UserTestCase(APIResponseTestCase):
    user_create_json = {
        'email': f'test_user4@example.com',
        'username': 'test_user_4',
        'first_name': 'test',
        'last_name': 'user',
        'password': 'foodgram_test',
    }

    @classmethod
    def setUpTestData(cls):
        cls.user1 = create_user('test_user_1')
        cls.user2 = create_user('test_user_2')
        cls.user3 = create_user('test_user_3')

    def test_list(self):
        self.assert_response(
            '/api/users/',
            expected_data={
                'results': [
                    get_user_json(user=self.user1),
                    get_user_json(user=self.user2),
                    get_user_json(user=self.user3)
                ]
            })

    def test_detail(self):
        self.assert_response(
            f'/api/users/{self.user1.pk}/',
            expected_data=get_user_json(user=self.user1))
        self.assert_response(
            f'/api/users/{self.user2.pk}/',
            expected_data=get_user_json(user=self.user2))
        self.assert_response(
            f'/api/users/{self.user3.pk}/',
            expected_data=get_user_json(user=self.user3))

    def test_detail_not_found(self):
        self.assert_response(
            '/api/users/99999999/',
            expected_status=status.HTTP_404_NOT_FOUND)

    def test_create(self):
        response = self.assert_response(
            '/api/users/', method='post',
            data=self.user_create_json,
            expected_status=status.HTTP_201_CREATED)
        self.assert_json_structure(response.data, {
            'id': int,
            'username': str,
            'email': str,
            'first_name': str,
            'last_name': str
        })

    def test_create_invalid(self):
        self.assert_invalid_data(
            '/api/users/', self.user_create_json)

    def test_profile(self):
        self.assert_response(
            '/api/users/me/',
            expected_data=get_user_json(user=self.user1),
            login_as=self.user1)

    def test_profile_no_auth(self):
        self.assert_response(
            '/api/users/me/',
            expected_status=status.HTTP_401_UNAUTHORIZED)

    def test_avatar(self):
        response = self.assert_response(
            '/api/users/me/avatar/', method='put',
            data={
                'avatar': 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAgMAAABieywaAAAACVBMVEUAAAD///9fX1/S0ecCAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOyYQAAAABJRU5ErkJggg=='
            },
            login_as=self.user1)
        self.assertRegex(response.data.get('avatar'), r'https?:\/\/[^\/]+\/media\/users\/.*\..*')

    def test_avatar_invalid(self):
        self.assert_response(
            '/api/users/me/avatar/', method='put',
            data={},
            expected_status=status.HTTP_400_BAD_REQUEST,
            login_as=self.user1)

    def test_avatar_delete(self):
        self.assert_response(
            '/api/users/me/avatar/', method='delete',
            expected_status=status.HTTP_204_NO_CONTENT,
            login_as=self.user1
        )

    def test_avatar_no_auth(self):
        self.assert_response(
            '/api/users/me/avatar/', method='put',
            expected_status=status.HTTP_401_UNAUTHORIZED)
        self.assert_response(
            '/api/users/me/avatar/', method='delete',
            expected_status=status.HTTP_401_UNAUTHORIZED)

    def test_password(self):
        self.assert_response(
            '/api/users/set_password/', method='post',
            data={
                'new_password': 'foodgram_test2',
                'current_password': 'foodgram_test'
            },
            expected_status=status.HTTP_204_NO_CONTENT,
            login_as=self.user1)

    def test_password_invalid(self):
        self.assert_invalid_data(
            '/api/users/set_password/',
            data={
                'new_password': 'foodgram_test2',
                'current_password': 'foodgram_test'
            },
            login_as=self.user1)

    def test_password_no_auth(self):
        self.assert_response(
            '/api/users/set_password/', method='post',
            expected_status=status.HTTP_401_UNAUTHORIZED)

    def test_token(self):
        response = self.assert_response(
            '/api/auth/token/login/', method='post',
            data={
                'email': 'test_user_1@example.com',
                'password': 'foodgram_test'
            })
        self.assertIsNotNone(response.data.get('auth_token', None))

    def test_token_delete(self):
        self.assert_response(
            '/api/auth/token/logout/', method='post',
            expected_status=status.HTTP_204_NO_CONTENT,
            login_as=self.user1)

    def test_token_delete_no_auth(self):
        self.assert_response(
            '/api/auth/token/logout/', method='post',
            expected_status=status.HTTP_401_UNAUTHORIZED)
