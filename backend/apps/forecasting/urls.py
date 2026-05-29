from django.urls import path

from .views import people_list, predict_duration, suppliers_list


urlpatterns = [
    path('predict/', predict_duration, name='forecast-predict'),
    path('people/', people_list, name='forecast-people'),
    path('suppliers/', suppliers_list, name='forecast-suppliers'),
]