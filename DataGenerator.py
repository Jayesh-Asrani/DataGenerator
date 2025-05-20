import json
from itertools import zip_longest
import argparse
import gzip
from faker import Faker
from datetime import datetime
import boto3
from confluent_kafka import Producer
import uuid

fake = Faker()


def generate_fields_config(config, field_expressions):
    start = 1
    for tuple in zip_longest(config['dimensionFieldSpecs'], config['metricFieldSpecs'], config['dateTimeFieldSpecs']):
        for element in tuple:
            if element is None:
                continue
            keyName = element['name']
            expression = element['config']['expression']
            if "fake" in expression:
                field_expressions[keyName] = expression
                continue
            else:
                match expression:
                    case "Sequence":
                        if "prefix" in element['config']:
                            field_expressions[keyName] = "Sequence-Prefix" + element['config']['prefix'] + "-" + str(
                                element['config']['cardinality'])
                        else:
                            field_expressions[keyName] = "Sequence-" + str(element['config']['cardinality'])
                        if start < element['config']['start']:
                            start = element['config']['start']
                    case "Increment":
                        field_expressions[keyName] = "Increment-"
                        if start < element['config']['start']:
                            start = element['config']['start']
    return start


def generate_data(noOfRecords, schemaName, connection, start):
    data = []
    batchSize = 1000000

    if connection["target"] == "Kafka":
        kafka_connection = dict(connection.copy())
        topic = kafka_connection["topic"]
        partitionKey = kafka_connection["partitionKey"]
        kafka_connection.pop("target")
        kafka_connection.pop("type")
        kafka_connection.pop("topic")
        kafka_connection.pop("partitionKey")
        kafka_connection["batch.size"] = batchSize
        producer = Producer(kafka_connection)

    for i in range(start, noOfRecords + start):
        record = {}
        for key in field_expressions:
            if "date_time" in field_expressions[key]:
                record[key] = str(eval(field_expressions[key]))
            elif "longitude" in field_expressions[key] or "latitude" in field_expressions[key]:
                record[key] = float(eval(field_expressions[key]))
            elif "Sequence-Prefix" in field_expressions[key]:
                prefix = field_expressions[key][15:field_expressions[key].rfind("-")]
                record[key] = prefix + str(i % int(field_expressions[key][field_expressions[key].rfind("-") + 1:]))
            elif "Sequence" in field_expressions[key]:
                record[key] = i % int(field_expressions[key][9:])
            elif "Increment" in field_expressions[key]:
                record[key] = i
            else:
                record[key] = eval(field_expressions[key])

        if connection["target"] == "Kafka":
            partitionKeyValue = record[partitionKey]
            push_to_kafka(producer, topic, partitionKeyValue, record)
            if i % batchSize == 0:
                producer.flush()
                print("Flushed Messages to Kafka")
        else:
            data.append(record)
            if i % batchSize == 0:
                fileName = schemaName + "_" + str(i) + ".json"
                write_file(fileName, data)
                if connection["target"] == "S3":
                    push_to_s3(fileName, data, connection)
                data = []

    if batchSize > noOfRecords and connection["target"] != "Kafka":
        write_file(schemaName + "_" + str(uuid.uuid4()) + ".json", data)
        if connection["target"] == "S3":
            push_to_s3(schemaName + ".json", data, connection)


def write_file(fileName, data):
    print("Data Generated for batch - Writing to File " + str(datetime.now()))
    data_bytes = json.dumps(data).encode('utf-8')
    with gzip.open(fileName + ".gzip", 'w') as f:
        f.write(data_bytes)
    print("Completed Writing to File " + str(datetime.now()))


def push_to_s3(fileName, data, connection):
    print("Writing to S3 " + str(datetime.now()))
    if "secretKey" in connection:
        s3 = boto3.client('s3', region_name=connection['region'], aws_access_key_id=connection["accessKey"],
                          aws_secret_access_key=connection["secretKey"])
    else:
        session = boto3.Session(profile_name=connection['profileName'])
        s3 = session.client('s3', region_name=connection['region'])

    objectname = connection['path'] + fileName + ".gzip"
    with open(fileName + ".gzip", "rb") as f:
        s3.upload_fileobj(f, connection['bucket'], objectname)


def push_to_kafka(producer, topic, partition_key, record):
    producer.produce(topic=topic, key=str(partition_key),
                     value=json.dumps(record), callback=acked)


def acked(err, msg):
    if err is not None:
        print(f"Failed to deliver message: {msg.value()}: {err.str()}")


def main():
    # Faker.seed(0)
    parser = argparse.ArgumentParser()
    parser.add_argument('-noOfRecords', '--noOfRecords')
    parser.add_argument('-configFile', '--configFile')
    args = parser.parse_args()

    print("Data Generator Started - " + str(datetime.now()))

    global field_expressions

    with open(args.configFile) as config_file:
        config = json.load(config_file)
    schemaName = config['schemaName']
    noOfRecords = int(args.noOfRecords)
    connection = config['connection']

    field_expressions = dict()
    start = generate_fields_config(config, field_expressions)

    if "cardinality" in config:
        cardinality = config['cardinality']
        seed = config['seed']

        j = int(100 / cardinality)

        for k in range(1, j + 1):
            Faker.seed(seed)
            generate_data(int(noOfRecords / j), schemaName, connection, int(start + (k * noOfRecords / j)))
    else:
        generate_data(noOfRecords, schemaName, connection, start)

    print("Data Generator Completed - " + str(datetime.now()))


if __name__ == "__main__":
    main()
