from .utils import APIResponseTestCase, status
from . import structs


def get_ingredient_url(ingredient_id):
    return f'/api/ingredients/{ingredient_id}/'


URL_INGREDIENTS = '/api/ingredients/'


class IngredientTestCase(APIResponseTestCase):
    def test_list(self):
        response = self.assert_response(
            URL_INGREDIENTS,
            expected_struct=[structs.ingredient])
        self.assertGreater(len(response.data), 0)

    def test_list_filter(self):
        response = self.assert_response(
            URL_INGREDIENTS + '?name=аб',
            expected_struct=[structs.ingredient])
        for item in response.data:
            self.assertTrue(item['name'].startswith('аб'))

    def test_detail(self):
        self.assert_response(
            get_ingredient_url(1),
            expected_struct=structs.ingredient)

    def test_detail_not_found(self):
        self.assert_response(
            get_ingredient_url(99999999),
            expected_status=status.HTTP_404_NOT_FOUND)
