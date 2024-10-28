import unittest

import pytest

from genetic_data.models import GeneticData, Individual
from src.genetic_data.constants import *
from src.genetic_data.genetic_data_parser import genetic_data_parser

class GeneticDataParserTests(unittest.TestCase):

    @pytest.mark.django_db
    def test_data_parser_ordering(self):
        data = ("#Chromosome,Variant ID,Position on chromosome,Alternate allele frequency,Reference allele,Alternate allele\n"
                "1,rs12345,1234567,0.12,A,G\n"
                "2,rs67890,2345678,0.34,C,T\n"
                "X,rs13579,3456789,0.45,G,A\n"
                "Y,rs24680,4567890,0.67,T,C")
        ind = Individual.objects.create(individual_id="123")
        genetic_data_parser(ind, data)
        genetic_data = GeneticData.objects.get(position="1234567")
        assert genetic_data.variant_id == "rs12345"
        assert genetic_data.alternate_frequency == "0.12"

    @pytest.mark.django_db
    def test_invalid_data_hash(self):
        data = ("#Variant ID,Chromosome,Position on chromosome,Reference allele,Alternate allele,Alternate allele frequency\n"
                "#rs12345,1,1234567,A,G,0.12")

        with self.assertRaises(Exception) as context:
            ind = Individual.objects.create(individual_id="123")
            genetic_data_parser(ind, data)

        self.assertTrue("Line incorrectly contains #: #rs12345,1,1234567,A,G,0.12" == str(context.exception))

    @pytest.mark.django_db
    def test_missing_data(self):
        data = ("#Variant ID,Chromosome,Position on chromosome,Reference allele,Alternate allele,Alternate allele frequency\n"
                "rs12345,1,1234567,A,G")

        with self.assertRaises(Exception) as context:
            ind = Individual.objects.create(individual_id="123")
            genetic_data_parser(ind, data)


        self.assertTrue("Data is missing on line 2" in str(context.exception))

    @pytest.mark.django_db
    def test_empty_data(self):
        data = ("#Variant ID,Chromosome,Position on chromosome,Reference allele,Alternate allele,Alternate allele frequency\n"
                "rs12345,1,1234567,,G,0.12")
        ind = Individual.objects.create(individual_id="123")

        with self.assertRaises(Exception) as context:
            genetic_data_parser(ind, data)


        self.assertTrue("Missing" in str(context.exception))

        data = ("#Variant ID,Chromosome,Position on chromosome,Reference allele,Alternate allele,Alternate allele frequency\n"
                ",1,1234567,A,G,0.12")

        with self.assertRaises(Exception):
            genetic_data_parser(ind, data)

        data = ("#Variant ID,Chromosome,Position on chromosome,Reference allele,Alternate allele,Alternate allele frequency\n"
                "rs12345,,1234567,A,G,0.12")

        with self.assertRaises(Exception):
            genetic_data_parser(ind, data)


        data = ("#Variant ID,Chromosome,Position on chromosome,Reference allele,Alternate allele,Alternate allele frequency\n"
                "rs12345,1,,A,G,0.12")

        with self.assertRaises(Exception):
            genetic_data_parser(ind, data)

        data = ("#Variant ID,Chromosome,Position on chromosome,Reference allele,Alternate allele,Alternate allele frequency\n"
                "rs12345,1,1234567,A,,0.12")

        with self.assertRaises(Exception):
            genetic_data_parser(ind, data)

        data = ("#Variant ID,Chromosome,Position on chromosome,Reference allele,Alternate allele,Alternate allele frequency\n"
                "rs12345,1,1234567,A,G,")

        with self.assertRaises(Exception):
            genetic_data_parser(ind, data)

    @pytest.mark.django_db
    def test_verify_variant_id(self):
        data = ("#Variant ID,Chromosome,Position on chromosome,Reference allele,Alternate allele,Alternate allele frequency\n"
                "rd12345,1,1234567,A,G,0.12")

        with self.assertRaises(Exception) as context:
            ind = Individual.objects.create(individual_id="123")
            genetic_data_parser(ind, data)


        self.assertTrue(f"Incorrect format for {VARIANT_ID} on line 2. Expecting format 'rs12345'" in str(context.exception))

    @pytest.mark.django_db
    def test_verify_chromosome(self):
        data = ("#Variant ID,Chromosome,Position on chromosome,Reference allele,Alternate allele,Alternate allele frequency\n"
                "rs12345,0,1234567,A,G,0.12")

        ind = Individual.objects.create(individual_id="123")
        
        with self.assertRaises(Exception) as context:
            genetic_data_parser(ind, data)


        self.assertTrue(f"Incorrect format for {CHROMOSOME} on line 2. Expecting the following values (1-22, X, Y)" in str(context.exception))

        data = ("#Variant ID,Chromosome,Position on chromosome,Reference allele,Alternate allele,Alternate allele frequency\n"
                "rs12345,23,1234567,A,G,0.12")

        with self.assertRaises(Exception):
            genetic_data_parser(ind, data)

        data = ("#Variant ID,Chromosome,Position on chromosome,Reference allele,Alternate allele,Alternate allele frequency\n"
                "rs12345,A,1234567,A,G,0.12")

        with self.assertRaises(Exception):
            genetic_data_parser(ind, data)

    @pytest.mark.django_db
    def test_verify_position(self):
        data = ("#Variant ID,Chromosome,Position on chromosome,Reference allele,Alternate allele,Alternate allele frequency\n"
                "rs12345,1,0,A,G,0.12")
        ind = Individual.objects.create(individual_id="123")

        with self.assertRaises(Exception) as context:
            genetic_data_parser(ind, data)

        self.assertTrue(f"Incorrect format for {POSITION} on line 2. Expecting value > 0" in str(context.exception))

        data = ("#Variant ID,Chromosome,Position on chromosome,Reference allele,Alternate allele,Alternate allele frequency\n"
                "rs12345,1,0.1,A,G,0.12")

        with self.assertRaises(Exception):
            genetic_data_parser(ind, data)

        data = ("#Variant ID,Chromosome,Position on chromosome,Reference allele,Alternate allele,Alternate allele frequency\n"
                "rs12345,1,invalid,A,G,0.12")

        with self.assertRaises(Exception):
            genetic_data_parser(ind, data)

    @pytest.mark.django_db
    def test_verify_reference(self):
        data = ("#Variant ID,Chromosome,Position on chromosome,Reference allele,Alternate allele,Alternate allele frequency\n"
                "rs12345,1,1234567,B,G,0.12")

        ind = Individual.objects.create(individual_id="123")
        
        with self.assertRaises(Exception) as context:
            genetic_data_parser(ind, data)


        self.assertTrue(f"Incorrect format for {REFERENCE} on line 2. Expecting values in [A, C, G, T]." in str(context.exception))

        data = ("#Variant ID,Chromosome,Position on chromosome,Reference allele,Alternate allele,Alternate allele frequency\n"
                "rs12345,1,1234567,AB,G,0.12")

        with self.assertRaises(Exception) as context:
            genetic_data_parser(ind, data)

    @pytest.mark.django_db
    def test_verify_alternate(self):
        data = ("#Variant ID,Chromosome,Position on chromosome,Reference allele,Alternate allele,Alternate allele frequency\n"
                "rs12345,1,1234567,A,F,0.12")

        ind = Individual.objects.create(individual_id="123")

        with self.assertRaises(Exception) as context:
            genetic_data_parser(ind, data)


        self.assertTrue(f"Incorrect format for {ALTERNATE} on line 2. Expecting values in [A, C, G, T]." in str(context.exception))

        data = ("#Variant ID,Chromosome,Position on chromosome,Reference allele,Alternate allele,Alternate allele frequency\n"
                "rs12345,1,1234567,A,GA,0.12")

        with self.assertRaises(Exception) as context:
            genetic_data_parser(ind, data)

    @pytest.mark.django_db
    def test_verify_alternate_freq(self):
        data = ("#Variant ID,Chromosome,Position on chromosome,Reference allele,Alternate allele,Alternate allele frequency\n"
                "rs12345,1,1234567,A,G,0")
        ind = Individual.objects.create(individual_id="123")

        with self.assertRaises(Exception) as context:
            genetic_data_parser(ind, data)


        self.assertTrue(f"Incorrect format for {ALTERNATE_FREQ} on line 2. Expecting values between 0 and 1." in str(context.exception))

        data = ("#Variant ID,Chromosome,Position on chromosome,Reference allele,Alternate allele,Alternate allele frequency\n"
                "rs12345,1,1234567,A,G,1")

        with self.assertRaises(Exception):
            genetic_data_parser(ind, data)