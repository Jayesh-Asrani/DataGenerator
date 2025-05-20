
# Data Generator

Data Generator is a Python package that generates fake data for pinot using faker library completely driven by configurations and copies that data onto an S3 bucket or a Kafka Topic


## Dependencies

``` pip install faker```
``` pip install boto3```
``` pip install confluent_kafka```


## Runtime Parameters

    1. --noOfRecords : Total Number of records to be generated
    2. --configFile : Location of the Json Config config file

\
e.g.  ``` --noOfRecords=100000 --configFile=Config/SampleSchema-S3-AWSProfile.json``` 

## Config File

The base of the config file is exactly similar to Pinot Schema Json file with an additional key 'connection' for copying the data onto Files/S3/Kafka

Base Parameters :

    1. seed : Seed produces the same result if same value used across executions. Possible values can be any integer
    2. cardinality : To set the default cardinality for the fields. Possible values : 25/40/50/75

    Note : If cardinality is provided seed is a mandatory parameter

Connection Parameters : 

    1. target : Destionation of the generated data. Possible values : File/S3/Kafka
    2. type : Type of data generated. Only JSON supported currently 
    3. Destination Specific keys : Depending upon the destination and authentication mechanism provide additional attributes

E.g : 

    "connection": {
        "target": "Kafka",
        "type": "JSON",
        "topic": "DataGenerator",
        "partitionKey": "UUID",
        "bootstrap.servers": "pkc-n00kk.us-east-1.aws.confluent.cloud:9092",
        "security.protocol": "SASL_SSL",
        "sasl.mechanisms": "PLAIN",
        "sasl.username": "",
        "sasl.password": ""
    }
Confif Parameters per field :

    1. config.expression : We can leverage any provider available as part of the faker library directly (https://faker.readthedocs.io/en/stable/providers.html)


## Usage/Examples Config

1. Generate a random sentence  
                                                                                            
        {
        "name": "Sentence",
        "dataType": "STRING",
        "config": {
            "expression": "fake.sentence()"
            }
        }

1. Generate a uuid  
                                                                                            
        {
        "name": "UUID",
        "dataType": "STRING",
        "config": {
            "expression": "fake.uuid4()"
             }
        }

1. Generate a random Integer  
                                                                                            
        {
        "name": "RandomInt",
        "dataType": "LONG",
        "config": {
            "expression": "fake.random.randint(1,100)"
            }
        }

1. Generate a random Decimal  
                                                                                            
        {
        "name": "DECIMAL",
        "dataType": "DECIMAL",
        "config": {
            "expression": "fake.random.randint(100,1000)/100"
            }
        }

1. Generate a random date_time  
                                                                                            
        {
        "name": "created_at",
        "dataType": "STRING",
        "config": {
            "expression": "fake.date_time()"
            }
        }

1. Generate a random epoch  
                                                                                            
        {
        "name": "created_at_datetime",
        "dataType": "LONG",
        "format": "1:MILLISECONDS:EPOCH",
        "granularity": "1:MILLISECONDS",
        "config": {
            "expression": "fake.unix_time()"
            }
        }

1. Generate a random datetime between a date and now  
                                                                                            
        {
        "name": "row_refreshed_at",
        "dataType": "STRING",
        "format": "SIMPLE_DATE_FORMAT|yyyy-MM-dd'T'HH:mm:ss.SSSZ",
        "granularity": "MILLISECONDS|1",
        "config": {
            "expression": "fake.date_time_between(datetime(2022, 3, 31))"
            }
        }

1. Generate a random boolean  
                                                                                            
        {
        "name": "is_updated",
        "dataType": "BOOLEAN",
        "config": {
            "expression": "fake.boolean()"
        }
        }


1. Generate a Incrementing Integer  
                                                                                            
        {
        "name": "Increment",
        "dataType": "LONG",
        "config": {
            "expression": "Increment",
            "start": 1
            }
        }


1. Generate a Sequence with specific cardinality  
                                                                                            
        {
        "name": "Sequence",
        "dataType": "LONG",
        "config": {
            "expression": "Sequence",
            "start": 1,
            "cardinality": 1000
            }
        }

1. Generate a Sequence with specific cardinality and a prefix
                                                                                            
        {
        "name": "Sequence_Prefix",
        "dataType": "STRING",
        "config": {
            "expression": "Sequence",
            "start": 200,
            "cardinality": 1000,
            "prefix": "Cust_"
            }
        }

1. choose a random element from list
                                                                                            
        {
        "name": "Choice",
        "dataType": "STRING",
        "config": {
            "expression": "fake.random_element([\"1\", \"2\"])"
            }
        }
## How to Execute

```python3 DataGenerator.py --noOfRecords=100000 --configFile=Config/SampleSchema-S3-AWSProfile.json```