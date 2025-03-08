# Spotify Charts Pipeline

A data pipeline that extracts and processes Spotify chart data to power an analytics dashboard.

## Overview

This pipeline retrieves data from the Spotify Charts API, processes it, and stores it in an **Amazon Redshift** data warehouse. The data is then transformed to generate structured tables for a dashboard that provides insights into trending music.

### Who is this for?

The dashboard is designed for record labels, artist managers, and music marketers looking to make data-driven decisions and need a high-level overview of pop music trends. It helps inform release strategies and marketing decisions by answering key business questions such as:

1. When is the best time to release music?
2. How do songs perform over time, and when should marketing efforts be applied?
3. Which are the highest performing songs and artists?

By leveraging these insights, industry professionals can make informed decisions about song releases, promotional strategies, and artist development.

### Architecture

![image info](./images/architecture.jpg)

### Data Model

The Entity Relational Diagram (ERD) for the data warehouse is:

![image info](./images/db_diagram.png)

## Result

![image info](./images/dashboard.jpg)

## Setup

### Pre-requisites

Ensure you have the following installed and configured:
- [Amazon Web Services (AWS)](https://aws.amazon.com/resources/create-account/) account
- [AWS Command Line Interface (AWS CLI)](https://docs.aws.amazon.com/streams/latest/dev/setup-awscli.html)
- [Terraform](https://developer.hashicorp.com/terraform/tutorials/aws-get-started/install-cli)
- [Docker Desktop](https://www.docker.com/get-started/)

### Running Pipeline

1. **Deploy AWS Resources**
    ```sh
    make terraform_deploy
    ```
    - Sets up necessary AWS services, including a randomised password for Amazon Redshift
    - Outputs configuration details for the pipeline

2. **Build the Docker Image**
    ```sh
    make build
    ```
    - Builds the Docker image with all project depedencies

3. **Run the Pipeline**
    ```sh
    make up
    ```
    - Retrieves a fresh Spotify API access token
    - Executes the data extraction, load and transformation process

### Stopping the Pipeline

1. **Stop Docker Containers**
    ```sh
    make down
    ```
    - Stops the running Docker image

2. **Destroy AWS Resources**
    ```sh
    make terraform_destroy
    ```
    - Stops and destroys the AWS services and infrastructure
