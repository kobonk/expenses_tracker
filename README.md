# Expenses Tracker Backend

The application serves as a backend for Expenses Tracker web app. It exposes REST API for retrieving and storing expense data.

## Installation

First you need a virtual environment for your application. It provides you a separate _sandbox_ environment to which you can install various dependencies and packages without conflicting with your global environment.

    python -m venv <location_to_which_the_virtual_environment_will_be_created>

Afret the environment is created it should be activated.

    <location_of_your_virtual_environment>/Scripts/activate

This command activates the environment and only after that you should do any development of the code.

Next you will need to install the necessary dependencies. They are listed in `requirements.txt` file.

    pip install -r requirements.txt

## Setup

For the application to work properly you need to initialize it with a script.

    python setup.py develop

This will create necessary links between local dependencies of the application.

## Running

Finally, to run the application you need only to execute the following command.

    python main.py
