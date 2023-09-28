"""
    This program listens for work messages contiously. 
    Start multiple versions to add more workers.  

    Author: Jordan Wheeler
    Date: 28 September 2023


"""

import pika
import sys
from collections import deque

# Import function for sending email
from email_alert import createAndSendEmailAlert

# Configure logging
from util_logger import setup_logger

logger, logname = setup_logger(__file__)

# Declare Deque Length
foodA_DEQUE = deque(maxlen=20)

# define a callback function to be called when a message is received
def foodA_callback(ch, method, properties, body):
    """ Define behavior on getting a message."""
    # decode the binary message body to a string
    logger.info(f" [x] Received {body.decode()}")

    # Setup Callback Information
    
    try: 
        # Smoker Message
        foodA_message = body.decode().split(",")
        # Check for valid temperatures
        if foodA_message[1] != 'No Reading':
            # Convert to float
            foodA_temp = float(foodA_message[1])
            # Check for valid timestamp
            foodA_timestamp = foodA_message[0]
            # Append to Deque
            foodA_DEQUE.append(foodA_temp)
            
            # Check for temperature change from previous temperatures 
            if len(foodA_DEQUE) >= 20:
                temperature_change = foodA_DEQUE[-1] - foodA_DEQUE[0]

            # Check for temperature change from previous temperatures outside tolerable (15)
            if abs(temperature_change) < 1:
                logger.info(F"Food A Temperature Alert at {foodA_timestamp}", "Food A Temperature Has Changed Less than 1 Degree.")
                alert_message = True
                
                if alert_message:
                    # Send Email Alert
                    email_subject = f"FoodA Temperature Alert at {foodA_timestamp}"
                    email_body = f"Food A Temperature Alerted That It Has Changed Less than 1 Degree in the last 10 minutes at {foodA_timestamp} indicating a stall."
                    createAndSendEmailAlert(email_subject, email_body)
                    # Reset alert message
                    alert_message = False
        # Send Confirmation Report
        logger.info("[X] FoodA Temperature Received and Processed.")
        # Delete Message from Queue after Processing
        ch.basic_ack(delivery_tag=method.delivery_tag)
    
    except Exception as e:
        logger.error("An Error Occured While Processing FoodA Temperature.")
        logger.error(f"The error says: {e}")
    

# define a main function to run the program
def main(hn: str = "localhost", qn: str = "task_queue"):
    """ Continuously listen for task messages on a named queue."""

    # when a statement can go wrong, use a try-except block
    try:
        # try this code, if it works, keep going
        # create a blocking connection to the RabbitMQ server
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=hn))

    # except, if there's an error, do this
    except Exception as e:
        print()
        logger.error("ERROR: connection to RabbitMQ server failed.")
        logger.error(f"Verify the server is running on host={hn}.")
        logger.error(f"The error says: {e}")
        print()
        sys.exit(1)

    try:
        # use the connection to create a communication channel
        channel = connection.channel()

        # use the channel to declare a durable queue
        # a durable queue will survive a RabbitMQ server restart
        # and help ensure messages are processed in order
        # messages will not be deleted until the consumer acknowledges
        channel.queue_declare(queue=qn, durable=True)

        # The QoS level controls the # of messages
        # that can be in-flight (unacknowledged by the consumer)
        # at any given time.
        # Set the prefetch count to one to limit the number of messages
        # being consumed and processed concurrently.
        # This helps prevent a worker from becoming overwhelmed
        # and improve the overall system performance. 
        # prefetch_count = Per consumer limit of unaknowledged messages      
        channel.basic_qos(prefetch_count=1) 

        # configure the channel to listen on a specific queue,  
        # use the callback function named callback,
        # and do not auto-acknowledge the message (let the callback handle it)
        channel.basic_consume( queue=qn, on_message_callback=foodA_callback, auto_ack=False)

        # print a message to the console for the user
        logger.info(" [*] Ready for work. To exit press CTRL+C")

        # start consuming messages via the communication channel
        channel.start_consuming()

    # except, in the event of an error OR user stops the process, do this
    except Exception as e:
        print()
        logger.error("ERROR: something went wrong.")
        logger.error(f"The error says: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print()
        logger.info(" User interrupted continuous listening process.")
        sys.exit(0)
    finally:
        logger.info("\nClosing connection. Goodbye.\n")
        connection.close()


# Standard Python idiom to indicate main program entry point
# This allows us to import this module and use its functions
# without executing the code below.
# If this is the program being run, then execute the code below
if __name__ == "__main__":
    # call the main function with the information needed
    main("localhost", "02-food-A")
