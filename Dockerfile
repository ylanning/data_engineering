ARG AIRFLOW_VERSION=2.9.2
ARG PYTHON_VERSION=3.12

FROM apache/airflow:${AIRFLOW_VERSION}-python${PYTHON_VERSION}

ENV AIRFLOW_HOME=/opt/airflow

# Install SSL certificates as root
USER root
RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates && rm -rf /var/lib/apt/lists/*
USER airflow

# Install project dependencies using pip (exported from Poetry)
COPY requirements-main.txt ./
RUN pip install --no-cache-dir --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org -r requirements-main.txt

# Copy the rest of your project files into the container
COPY . .
