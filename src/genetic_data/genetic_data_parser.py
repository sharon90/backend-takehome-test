from rest_framework.exceptions import ValidationError

from genetic_data.models import GeneticData
from genetic_data.constants import *

def genetic_data_parser(individual_id, data: str):
    """
    Takes the individual id and data from file. Then creates GeneticData in database for each line

    :param individual_id:
    :param data:
    :return: None
    """
    column_positions: dict = {}
    lines = data.splitlines()
    for line_no in range(len(lines)):
        if lines[line_no][0] == "#":
            if len(column_positions.keys()) != 0: # check if data incorrectly starts with hash
                raise Exception(f"Line incorrectly contains #: {lines[line_no]}")

            line = lines[line_no][1:] # remove the hash
            headers = line.split(",")
            count = 0
            for header in headers:
                column_positions[header] = count
                count += 1
            continue

        data_values = lines[line_no].split(",")

        if len(data_values) != len(column_positions.keys()):
            raise Exception(f"Data is missing on line {line_no + 1}: {lines[line_no]}")

        # find the column position, then get and store the value at the position
        variant_id = data_values[column_positions[VARIANT_ID]]
        chromosome = data_values[column_positions[CHROMOSOME]]
        position = data_values[column_positions[POSITION]]
        reference_allele = data_values[column_positions[REFERENCE]]
        alternate_allele = data_values[column_positions[ALTERNATE]]
        alternate_frequency = data_values[column_positions[ALTERNATE_FREQ]]

        validate(variant_id, chromosome, position, reference_allele, alternate_allele, alternate_frequency, line_no + 1)

        GeneticData.objects.create(individual_id=individual_id,
                                   variant_id=variant_id,
                                   chromosome=chromosome,
                                   position=position,
                                   reference_allele=reference_allele,
                                   alternate_allele=alternate_allele,
                                   alternate_frequency=alternate_frequency)


# move this function to be used as part of pre_save function for GeneticData model
def validate(variant_id, chromosome, position, reference, alternate_allele, alternate_allele_frequency, line_no: int):
    if variant_id == "":
        raise Exception(f"Missing {VARIANT_ID} on line {line_no}")

    if not variant_id.startswith("rs"):
        raise ValidationError(f"Incorrect format for {VARIANT_ID} on line {line_no}. Expecting format 'rs12345'. Got {variant_id}")

    if chromosome == "":
        raise Exception(f"Missing {CHROMOSOME} on line {line_no}")

    # Given more time, I'd improve this test here so it's clear if it's a string or a number and will check better.
    # E.g. currently returns ValueError instead of ValidationError if chromosome value is Z
    if chromosome not in ("X", "Y") and not 1 <= int(chromosome) <= 22:
        raise ValidationError(f"Incorrect format for {CHROMOSOME} on line {line_no}. Expecting the following values (1-22, X, Y). Got {chromosome}")

    if position == "":
        raise Exception(f"Missing {POSITION} on line {line_no}")

    if int(position) <= 0:
        raise ValidationError(f"Incorrect format for {POSITION} on line {line_no}. Expecting value > 0. Got {position}")

    if reference == "":
        raise Exception(f"Missing {REFERENCE} on line {line_no}")

    if reference not in ["A", "C", "G", "T"]:
        raise ValidationError(f"Incorrect format for {REFERENCE} on line {line_no}. Expecting values in [A, C, G, T]. Got {reference}")

    if alternate_allele == "":
        raise Exception(f"Missing {ALTERNATE} on line {line_no}")

    if alternate_allele not in ["A", "C", "G", "T"]:
        raise ValidationError(f"Incorrect format for {ALTERNATE} on line {line_no}. Expecting values in [A, C, G, T]. Got {alternate_allele}")

    if alternate_allele_frequency == "":
        raise Exception(f"Missing {ALTERNATE_FREQ} on line {line_no}")

    if not 0 < float(alternate_allele_frequency) < 1:
        raise ValidationError(f"Incorrect format for {ALTERNATE_FREQ} on line {line_no}. Expecting values between 0 and 1. Got {alternate_allele_frequency}")