user_short = {
    'id': int,
    'username': str,
    'email': str,
    'first_name': str,
    'last_name': str
}
user = user_short | {
    'is_subscribed': bool,
    'avatar': str
}

ingredient = {
    'id': int,
    'name': str,
    'measurement_unit': str
}
recipe_ingredient = ingredient | {
    'amount': int
}

recipe_short = {
    'id': int,
    'name': str,
    'image': str,
    'cooking_time': int
}
recipe = recipe_short | {
    'text': str,
    'is_favorited': bool,
    'is_in_shopping_cart': bool,
    'author': user,
    'ingredients': [recipe_ingredient]
}
