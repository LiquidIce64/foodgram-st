from rest_framework.filters import BaseFilterBackend, SearchFilter


def param_equals(request, param, value):
    return request.query_params.get(param, '') == value


def param_get_id(request, param):
    value = request.query_params.get(param, '')
    try:
        return int(value)
    except ValueError:
        return None


class RecipeFilterBackend(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        filter_author = param_get_id(request, 'author')
        filter_cart = param_equals(request, 'is_in_shopping_cart', '1')
        filter_favorites = param_equals(request, 'is_favorited', '1')

        if filter_author is not None:
            queryset = queryset.filter(author__pk=filter_author)

        if request.user.is_authenticated:
            if filter_cart:
                queryset = queryset.filter(
                    in_shopping_carts__user=request.user)
            if filter_favorites:
                queryset = queryset.filter(
                    favorites__user=request.user)
        elif filter_cart or filter_favorites:
            queryset = queryset.none()

        return queryset


class NameSearchFilter(SearchFilter):
    search_param = 'name'

    def get_search_fields(self, view, request):
        return ('^name',)
