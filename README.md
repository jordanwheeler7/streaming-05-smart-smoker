# streaming-05-smart-smoker
- [Jordan Wheeler](https://github.com/jordanwheeler7)
- CSIS 44671: Streaming Data
- Module 5: Creating a Producer
- 19 September 2023
- [Github Pages]()

## Overview
This repository serves as an example of streaming data. We demonstrate the process, design our system, and implement the producer. In this project, we create a producer to send three different temperature readings to consumers. Channel 1 tells us the temperature of the smoker itself. Channels 2 & 3 read the temperatures of two different meats. Utilizing RabbitMQ, we send this information to the different consumers for us to be able to analyze.
[Data Source](smoker-temps.csv)

## Create a Virtual Environment
1. Open a terminal window
2. Navigate to the project folder
3. Type `python -m venv .venv` to create a virtual environment
4. Type `source .venv/bin/activate` to activate the virtual environment

## Requirements
1. Git
2. Python 3.7+ (3.11+ preferred)
3. VS Code Editor
4. VS Code Extension: Python (by Microsoft)
5. RabbitMQ Server installed and running locally
6. Pika installed into the virtual environment


## Running the Code
Open up a terminal window and navigate to the file in which you have saved the repository (I use `cd C:\Users\{filepath}`). Once there, start running your virtual environment. Once activated, run `python message_producer.py`. The file will ask you if you want to open RabbitMQ in admin mode, type y for yes and n for no; "guest" is the name and password. Once activated, the file will produce a message every 30 seconds, and a confirmation is sent. Due to this being a durable queue, the file will continue to run until it reaches the end or the user enters `Ctrl + C`. Once ended the queue will be deleted and start again upon the next activation.

## Screenshots of Running Code
