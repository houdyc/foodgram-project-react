from django.http.response import HttpResponse
from django.utils import timezone


def make_txt_response(ingredients):
    shopping_list = 'Купить в магазине:\n'
    for ingredient in ingredients:
        shopping_list += (
            f'{ingredient["ingredient__name"]}: '
            f'({ingredient["ingredient__measurement_unit"]})'
            f' - {ingredient["amount"]} \n'
        )
    now = timezone.now()
    file_name = f'ingredients list{now:%Y-%m-%d}'
    response = HttpResponse(shopping_list, content_type='text/plain')
    response['Content-Disposition'] = (
        f'attachment; filename="{file_name}.txt"')
    return response
