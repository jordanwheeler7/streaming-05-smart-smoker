"""
    This program sends a message to a queue on the RabbitMQ server.
    It simulates temperatures being relayed from a smoker to a server.

    Author: Jordan Wheeler
    Date: 19 September 2023
"""

import pika
import sys
import webbrowser
import csv
import time


# Configure logging
from util_logger import setup_logger

logger, logname = setup_logger(__file__)

SHOW_OFFER = True

def offer_rabbitmq_admin_site():
    """Offer to open the RabbitMQ Admin website"""
    ans = input("Would you like to monitor RabbitMQ queues? y or n ")
    logger.info("Seeing if you want to monitor RabbitMQ queues")
    if ans.lower() == "y":
        webbrowser.open_new("http://localhost:15672/#/queues")
        logger.info(f"Answer is {ans}.")

def send_message(host: str, first_queue_name: str, second_queue_name: str, third_queue_name: str, input_file: str):
    """
    Creates and sends a message to the queue each execution.
    This process runs and finishes.

    Parameters:
        host (str): the host name or IP address of the RabbitMQ server
        queue_names (str): the names of the queue's to send the message to
        input_file: the name of the file to read the messages from
    """

    try:
        # create a blocking connection to the RabbitMQ server
        conn = pika.BlockingConnection(pika.ConnectionParameters(host))
        # use the connection to create a communication channel
        ch = conn.channel()
        
        # delete the queue if it already exists
        # this is a convenience to clear the queue before running        
        ch.queue_delete(queue=first_queue_name)
        ch.queue_delete(queue=second_queue_name)
        ch.queue_delete(queue=third_queue_name)
        # use the channel to declare a durable queue
        # a durable queue will survive a RabbitMQ server restart
        # and help ensure messages are processed in order
        # messages will not be deleted until the consumer acknowledges
        ch.queue_declare(queue=first_queue_name, durable=True)
        ch.queue_declare(queue=second_queue_name, durable=True)
        ch.queue_declare(queue=third_queue_name, durable=True)
        # Read the tasks.csv file and send each task to the queue
        with open(input_file, 'r') as input_file:
            reader = csv.reader(input_file)
            # skip the header row
            header = next(reader)
            logger.info("Skipping header row")
            # for each row in the file
            for row in reader:
                # get row variables
                time_stamp, smoker_temp, foodA, foodB = row
                
                # Ensure our temperatures have a reading
                if smoker_temp == '':
                    smoker_temp = 'No Reading'
                if foodA == '':
                    foodA = 'No Reading'
                if foodB == '':
                    foodB = 'No Reading'
                
            
           
                # create a message to send to the queue
                message1 = time_stamp, smoker_temp
                message2 = time_stamp, foodA
                message3 = time_stamp, foodB
                
                # encode the messages
                message1_encode = "," .join(message1).encode()
                message2_encode = "," .join(message2).encode()
                message3_encode = "," .join(message3).encode()              
                
                # use the channel to publish a message to the queue
                # every message passes through an exchange
                ch.basic_publish(exchange="", routing_key=first_queue_name, body=message1_encode)
                # print a message to the console for the user
                logger.info(f" [x] Sent {message1} to {first_queue_name}")
                # use the channel to publish a message to the queue
                ch.basic_publish(exchange="", routing_key=second_queue_name, body=message2_encode)
                # print a message to the console for the user
                logger.info(f" [x] Sent {message2} to {second_queue_name}")
                # use the channel to publish a message to the queue
                ch.basic_publish(exchange="", routing_key=third_queue_name, body=message3_encode)
                # print a message to the console for the user
                logger.info(f" [x] Sent {message3} to {third_queue_name}")
                # Wait 30 seconds between each message
                time.sleep(30)
                
    except pika.exceptions.AMQPConnectionError as e:
        logger.error(f"Error: Connection to RabbitMQ server failed: {e}")
        sys.exit(1)
    finally:
        # close the connection to the server
        conn.close()

# Standard Python idiom to indicate main program entry point
# This allows us to import this module and use its functions
# without executing the code below.
# If this is the program being run, then execute the code below
if __name__ == "__main__":  
    # See if offer_rabbitmq_admin_site() should be called
    if SHOW_OFFER == True:
        # ask the user if they'd like to open the RabbitMQ Admin site
        offer_rabbitmq_admin_site()
    # send the message to the queue
    send_message("localhost","01-smoker","02-food-A","03-food-B","smoker-temps.csv")  