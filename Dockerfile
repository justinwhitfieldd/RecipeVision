# Use an official Python runtime as the base image
FROM python:3.11.6

RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx

# Set the working directory in the container to /app
WORKDIR /app
ENV APP_HOME /app
ENV PORT 5000

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Define environment variable
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 main:app

# Run your_flask_app.py when the container launches
CMD ["flask", "run"]