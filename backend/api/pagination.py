from rest_framework.pagination import PageNumberPagination


class CustomPageNumberPagination(PageNumberPagination):
    """это пользовательский класс пагинации, который расширяет
    функциональность стандартного класса пагинации PageNumberPagination из
    фреймворка Django REST Framework"""

    # Указываем параметр запроса, который будет определять количество
    # элементов на странице
    page_size_query_param = "limit"

    # Оптимизация для уменьшения нагрузки на базу данных
    max_page_size = 100

    # Оптимизация для ускорения рендеринга страницы
    page_size = 20
