from django.urls import path

from genetic_data.views import GeneticDataView, IndividualView

urlpatterns = [
    path("", IndividualView.as_view(), name='individual_data'),
    path("/<individual_id>/genetic-data", GeneticDataView.as_view(), name='genetic_data')
]
