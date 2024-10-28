import json

from django.http import HttpResponse
from rest_framework import generics

from genetic_data.models import GeneticData, Individual
from django.core import serializers

from genetic_data.genetic_data_parser import genetic_data_parser


# Given more time, I will add authentication and more data sanitization. Admin users will have authorisation to PATCH and DELETE data etc..
# I would also improve the GET and POST return payload so it's easily understandable and only returns relevant fields.
# I will also improve error handling with better error messages. Do a try/except and return the appropriate error to user where necessary.

class IndividualView(generics.GenericAPIView):
    def get(self, request):
        data = serializers.serialize('json', Individual.objects.all())
        return HttpResponse(json.dumps(data), content_type = 'application/json')

    def post(self, request):
        new_id = request.data.get('id')

        if not new_id or new_id == '' or len(new_id.split(" ")) > 1:
             return HttpResponse(status=400, content="POST should be in the format 'id=<id>'")

        individual = Individual.objects.create(individual_id=new_id)
        return HttpResponse(status=201, content=f"Created Individual with id '{individual.individual_id}'")

class GeneticDataView(generics.GenericAPIView):
    def get(self, request, individual_id):
        queryset = GeneticData.objects.filter(individual_id=individual_id)
        queries = self.request.GET.get('variants', None)
        if queries is not None:
            queryset = queryset.filter(variant_id__in=queries.split(','))
        data = serializers.serialize('json', queryset.order_by('-created'))
        return HttpResponse(json.dumps(data), content_type = 'application/json')

    def post(self, request, individual_id):
        path = request.data.get('file')
        if not path or path == '':
            return HttpResponse(status=400, content="POST should be in the format 'file=<file-path>'")

        individual = Individual.objects.get(individual_id=individual_id)
        with open(path, 'r') as data:
            genetic_data_parser(individual, data.read())

        return HttpResponse(status=201)