from .utils import APIResponseTestCase, status


class IngredientTestCase(APIResponseTestCase):
    json_structure = {
        'id': int,
        'name': str,
        'measurement_unit': str
    }

    def test_list(self):
        response = self.assert_response('/api/ingredients/')
        self.assertIsInstance(response.data, list)
        self.assertGreater(len(response.data), 0)
        self.assert_json_structure(response.data[0], self.json_structure)

    def test_detail(self):
        response = self.assert_response('/api/ingredients/1/')
        self.assert_json_structure(response.data, self.json_structure)

    def test_detail_not_found(self):
        self.assert_response(
            '/api/ingredients/99999999/',
            expected_status=status.HTTP_404_NOT_FOUND)
