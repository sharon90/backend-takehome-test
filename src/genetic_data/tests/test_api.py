import codecs
import os
import unittest

import pytest
from django.test import Client

from genetic_data.models import GeneticData, Individual


class APITests(unittest.TestCase):
    @pytest.mark.django_db
    def test_get_all_individuals(self):
        i = Individual.objects.create(individual_id="test123")


        c = Client()
        response = c.get("/individuals")
        assert response.status_code == 200
        assert i.individual_id in str(response.content)

    @pytest.mark.django_db
    def test_post_individuals(self):
        c = Client()
        response = c.post("/individuals", data={"id":"testing"})

        id = codecs.decode(response.content,'utf-8')

        assert response.status_code == 201
        assert Individual.objects.filter(individual_id=id.split("'")[1]).count() > 0

    @pytest.mark.django_db
    def test_get_all_genetic_data_for_specific_individual(self):
        i = Individual.objects.create(individual_id="test123")
        i2 = Individual.objects.create(individual_id="test567")
        genetic_data = GeneticData.objects.create(individual_id = i, variant_id="rs123")
        genetic_data2 = GeneticData.objects.create(individual_id = i2, variant_id="rs567")

        c = Client()

        response = c.get(f"/individuals/{i.individual_id}/genetic-data")

        assert genetic_data.variant_id in str(response.content)
        assert genetic_data2.variant_id not in str(response.content)

        genetic_data3 = GeneticData.objects.create(individual_id = i, variant_id="rs789")
        response = c.get(f"/individuals/{i.individual_id}/genetic-data?variants=rs789,rs451")
        assert genetic_data.variant_id not in str(response.content)
        assert genetic_data2.variant_id not in str(response.content)
        assert genetic_data3.variant_id in str(response.content)

    @pytest.mark.django_db
    def test_post_data_for_specific_individual(self):
        i = Individual.objects.create(individual_id="test123")

        c = Client()
        # assert we have no data here
        response = c.get(f"/individuals/{i.individual_id}/genetic-data")
        assert codecs.decode(response.content,'utf-8') == '"[]"'

        # assert data is then added
        root = os.path.dirname(os.path.abspath(__file__))
        response = c.post(f"/individuals/{i.individual_id}/genetic-data", data={"file":f"{root}/../../../individual123.sano"})
        assert response.status_code == 201

        response = c.get(f"/individuals/{i.individual_id}/genetic-data")
        assert codecs.decode(response.content,'utf-8') != '"[]"'
        assert "4567890" in str(response.content)