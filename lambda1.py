import json
import os
import boto3
from datetime import datetime

table_name = os.environ.get('TABLE')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(table_name)

def parse_number_word(word):
    import re

    # Basic mappings
    units = {
        "null": 0, "eins": 1, "ein": 1, "zwei": 2, "drei": 3, "vier": 4, "fünf": 5,
        "sechs": 6, "sieben": 7, "acht": 8, "neun": 9
    }

    teens = {
        "zehn": 10, "elf": 11, "zwölf": 12, "dreizehn": 13, "vierzehn": 14,
        "fünfzehn": 15, "sechzehn": 16, "siebzehn": 17, "achtzehn": 18, "neunzehn": 19
    }

    tens = {
        "zwanzig": 20, "dreißig": 30, "vierzig": 40, "fünfzig": 50,
        "sechzig": 60, "siebzig": 70, "achtzig": 80, "neunzig": 90
    }

    multipliers = {
        "hundert": 100,
        "tausend": 1000
    }
    word = word.lower()
    total = 0

    # Handle tausend
    if "tausend" in word:
        parts = word.split("tausend")
        thousand_part = parts[0]
        rest = parts[1]
        total += (parse_number_word(thousand_part) if thousand_part else 1) * 1000
        word = rest

    # Handle hundert
    if "hundert" in word:
        parts = word.split("hundert")
        hundred_part = parts[0]
        rest = parts[1]
        total += (parse_number_word(hundred_part) if hundred_part else 1) * 100
        word = rest

    # Handle teens
    if word in teens:
        return float(total + teens[word])

    # Handle tens with "und"
    match = re.match(r"(.+)und(.+)", word)
    if match:
        unit_part, ten_part = match.groups()
        if ten_part in tens and unit_part in units:
            return float(total + tens[ten_part] + units[unit_part])

    # Handle plain tens and units
    if word in tens:
        return float(total + tens[word])
    if word in units:
        return float(total + units[word])

    return float(total)

def lambda_handler(event, context):
    amount = event['amount'].split()[0]
    if amount.isdigit():
        amount = float(amount)
    elif "," in amount:
        amount = float(amount.replace(",", "."))
    else:
        amount = parse_number_word(amount)
    description = event['description']

    item = {
        'pk': 'marco_campini',
        'sk': datetime.utcnow().isoformat(),
        'amount': str(amount),
        'description': description
    }
    table.put_item(Item=item)
    return
