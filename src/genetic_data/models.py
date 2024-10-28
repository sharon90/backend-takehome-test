from django.db import models


class Individual(models.Model):
    individual_id = models.CharField(max_length=255, primary_key=True, unique=True)

class GeneticData(models.Model):
    id =  models.AutoField(primary_key=True, blank=True)
    individual_id = models.ForeignKey(Individual, on_delete=models.CASCADE)
    variant_id = models.CharField(max_length=255)
    chromosome = models.CharField(max_length=10)
    position = models.CharField(max_length=255)
    reference_allele = models.CharField(max_length=10)
    alternate_allele = models.CharField(max_length=10)
    alternate_frequency = models.CharField(max_length=10)
    created = models.DateTimeField(auto_now_add=True, blank=True)

