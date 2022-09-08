# Mini Kaggle (Also known as data-platform)

A Kaggle clone made using the Django framework as a learning project at Divar in the summer of 2021. This project is a collective work of 5 people, and its credits are divided between the members.

## Key Features

Featuring a robust authentication system, you can create your account and start analyzing datasets, create notebooks to work with those datasets, define workflows as DAGs, and recieve notifications corresponding to the state of your tasks.

We have implemented a Jupyter Notebook clone from scratch that runs within a safe, isolated Docker enviorement.

You can also define workflows. These can help you define a series of tasks to be done in a specific order and time so your data could be pipelined between notebooks. This way you don't have to stay awake at nights running your notebooks!

## How To Use

To run the mini-kaggle webapp, first you have to install the requirements. To do so, run:

    pip install -r requirements.txt

Then to run the project, simply run:

    ./manage.py migrate
    ./manage.py runserver

Keep in mind that the first line has to be run only once.

## Licence

All rights are reserved by the developers. For more information you can read [LICENCE](https://github.com/kamali-sina/mini-kaggle/blob/main/LICENCE).