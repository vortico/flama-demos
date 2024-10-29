## Welcome to **flama-demos** 🤗

This repository contains a collection of examples and demonstrations showcasing the usage of the [Flama](https://flama.dev/).

Flama 🔥 is a python library which establishes a **standard framework** for development and deployment of APIs with special focus on machine learning (ML). The main aim of the framework is to make **ridiculously simple** the deployment of **ML APIs**, simplifying (when possible) the entire process to a single line of code. This is a *Framework for the development of Lightweight Applications and Machine-learning Automation*.

For more information about Flama:

- **Flama Website:** [https://flama.dev/](https://flama.dev/)
- **GitHub Repository:** [https://github.com/vortico/flama](https://github.com/vortico/flama)

## Contents

This repository is organised to provide you with practical examples covering various aspects of Flama's capabilities. Whether you are interested in App development, deployment strategies, or leveraging machine learning APIs, you'll find relevant demos here. 

Whilst the demos are organised into numbered folders, they are not necessarily meant to be followed in any particular order. The only reason for the numbering is to show the order in which the demos were created and published.

The following demos are currently available:

- [**01-mlapi-sklearn-pipeline**](01-mlapi-sklearn-pipeline): This demo shows how to create a simple Machine Learning (ML) API using Flama and Scikit-Learn. In the demo, we build from scratch an ML pipeline with simple (yet realistic) data preprocessing, training, and prediction steps. The demo shows how to package the pipeline as an FLM (*Flama Lightweight Model*) and deploy it as a REST API. The demo also shows how to use the API to make predictions from a simple web application. Finally, we customise the API's documentation and add a custom endpoint to the builtin endpoints provided by Flama. This demo was published as a [blog post](https://dev.to/vortico/introducing-flama-for-robust-machine-learning-apis-b3n).
- [**02-jwt-protected-mlapis**](02-jwt-component): This demo shows how to secure a Machine Learning (ML) API using JSON Web Tokens (JWT). In the demo, we show how to add JWT-based authentication to the MLAPI with **flama** `JWTComponent`. We create a simple authentication system using JWT and secure the API's endpoints to only allow authenticated users to access them. This demo was published as a [blog post](https://dev.to/vortico/protected-ml-apis-with-flama-jwt-authentication-3emn).
- [**03-domain-driven-design**](03-domain-driven-design): This demo shows how to implement a simple Domain-Driven Design (DDD) architecture in a `Flama` application. In the demo, we create a simple application that models a user registration system using DDD principles. We show how to create a domain model, repositories, and services to handle user registration and authentication. This demo was published as a [blog post](https://dev.to/vortico/native-domain-driven-design-with-flama-l9o).

## Usage

Each demo folder contains a detailed README with instructions on how to run the example. Follow the steps outlined in the respective demo's `README` to explore and experiment with Flama.

## Contribution

We welcome contributions from the community! If you have additional demos, improvements, or bug fixes, feel free to open an issue or submit a pull request.

## License

This repository is licensed under the [Apache License, Version 2.0](https://www.apache.org/licenses/LICENSE-2.0). See the [`LICENSE`](LICENSE) file for more details.
