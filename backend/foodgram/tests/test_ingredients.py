from .utils import APIResponseTestCase, status


def get_ingredient_url(ingredient_id):
    return f'/api/ingredients/{ingredient_id}/'


URL_INGREDIENTS = '/api/ingredients/'

INGREDIENT_STRUCT = {
    'id': int,
    'name': str,
    'measurement_unit': str
}


class IngredientTestCase(APIResponseTestCase):
    def test_list(self):
        response = self.assert_response(URL_INGREDIENTS)
        self.assertIsInstance(response.data, list)
        self.assertGreater(len(response.data), 0)
        self.assert_json_structure(response.data[0], INGREDIENT_STRUCT)

    def test_detail(self):
        response = self.assert_response(get_ingredient_url(1))
        self.assert_json_structure(response.data, INGREDIENT_STRUCT)

    def test_detail_not_found(self):
        self.assert_response(
            get_ingredient_url(99999999),
            expected_status=status.HTTP_404_NOT_FOUND)
