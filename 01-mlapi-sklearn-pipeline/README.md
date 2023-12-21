# Introducing Flama for Robust Machine Learning APIs

Every time we use an application such as Instagram, Facebook, or Twitter, we are using an application programming interface (API) without even noticing it. APIs are everywhere, and they are the glue that connects the different services that we use every day in a seamless way.

This is precisely the reason why APIs are so important for software development. APIs allow developers to encapsulate functionality and expose it in a standardised way, so that other systems can consume it without having to know the details of the implementation. This is what we call *abstraction*.

For many years, APIs were mostly thought for exposing one of the following types of functionality:

- **Data manipulation**: APIs were also used to expose data, i.e. the information that is stored in a database. For example, the information about a user, or the information about a product.

- **Business logic**: APIs were also used to expose business logic, i.e. the rules that define how a business operates. For example, the rules that define how a user can buy a product, or the rules that define how a user can register in a system.

There has been a considerable effort in the last few years to try and standardise the way in which these type of APIs are implemented via different frameworks. However, over the last few years, a new type of functionality has become more and more popular: *machine learning (ML) models*; and the existing frameworks for building APIs are not well suited for this type of functionality. In this series of posts, we will learn how to build APIs using a *Framework for the development of Lightweight Applications and Machine-learning Automation*, also known as [Flama](https://flama.dev). 

**Flama** is an open-source Python library which establishes a standard framework for development and deployment of APIs with special focus on ML products. The main aim of **Flama** is to make ridiculously simple the deployment of ML APIs, simplifying (when possible) the entire process to a single line of code.

In particular, in this first post we are going to learn how to build a simple API which exposes:

- A simple *function* which returns a string, to show how to expose business logic via an API.
- A simple *machine learning model* (actually an ML pipeline) which returns a prediction given a certain input, to show how to expose ML models via an API.

In order to do so, we will discuss the following topics:

- [Setting up the development environment](#development-environment) 
- [Creating the project structure](#project-structure)
- [Installing `flama` and extra dependencies for ML](#installing-flama)
- [Creating an ML pipeline with `scikit-learn`](#ml-pipeline-with-scikit-learn)
- [Packaging the ML pipeline with `flama`](#packaging-the-ml-pipeline-flm-files)
- [Serving the ML pipeline without code](#serving-the-ml-pipeline-flama-cli)
- [Interacting the ML pipeline without server](#serverless-interaction-with-the-model)
- [Building an ML API using `flama`](#custom-ml-apis-with-flama)

We will finish this post with a [summary](#conclusions) of the main takeaways, and a list of [resources](#references) for further reading. Hope you enjoy it!

## Development environment

### Python version

When dealing with software development, reproducibility is key. This is why we encourage you to use Python virtual environments to set up an isolated environment for your project. Virtual environments allow the isolation of dependencies, which plays a crucial role to avoid breaking compatibility between different projects. We cannot cover all the details about virtual environments in this post, but we encourage you to learn more about [venv](https://docs.python.org/3/library/venv.html#module-venv), [pyenv](https://github.com/pyenv/pyenv) or [conda](https://docs.conda.io/en/latest/) for a better understanding on how to create and manage virtual environments.

To create and activate a virtual environment with a compatible Python version you can take the following code snippets. Before you start working on a new project, it is very important to activate the corresponding environment. The last command line in both code snippets precisely activate the environment with **pyenv** or **conda**, respectively. 

#### Creation of virtual environment with pyenv
```bash
pyenv install 3.11.5
pyenv virtualenv 3.11.5 flama-dev
pyenv local flama-dev
```

#### Creation of virtual environment with **conda**
```bash
conda create --name flama-dev python=3.11.5 --yes
conda activate flama-dev
```

Whilst you can use any tool to create and manage your virtual environments, we will be using **pyenv** throughout this series of posts. This is because **pyenv** is a lightweight tool which allows us to manage different Python versions and virtual environments in a very simple way, and it works great with **poetry** (which we will discuss later).

### Packaging and dependency management

Once you have created and activated your virtual environment, you can start installing the dependencies for your project. Whenever we start a new project, we typically need to install dependencies which are not part of the Python standard library. These dependencies can be manually installed using `pip` or `conda` (as you probably know already), but that means we have to keep track of the dependencies and their versions manually! This is not only tedious, but also error-prone, because third-party dependencies usually have their own requirements, which eventually can conflict with the requirements of other dependencies. This leads to the so-called [dependency hell](https://en.wikipedia.org/wiki/Dependency_hell), which is practically impossible to solve manually. This is where depenedency management tools come into play. These tools allow us to declare the dependencies of our project in a file (or via a simple command line), and they take care of looking for the correct versions of the dependencies and installing them for us, keeping track of the dependencies and their versions automatically. 

We believe that [poetry](https://python-poetry.org/) is currently the best tool for this purpose, besides of being the most popular one at the moment. This is why we will use **poetry** to manage the dependencies of our project throughout this series of posts. Poetry allows you to declare the libraries your project depends on, and it will manage (install/update) them for you. Poetry also allows you to package your project into a distributable format and publish it to a repository, such as [PyPI](https://pypi.org/). We strongly recommend you to learn more about this tool by reading the official [documentation](https://python-poetry.org/docs/). 

Thus, the first thing we need to do is to install **poetry** in our active virtual environment. Following the official [instructions](https://python-poetry.org/docs/#installing-with-the-official-installer), we can run the following command line:

#### Linux, macOS, Windows (WSL)
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

#### Windows (PowerShell)
```bash
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -
```

Once installed, you should follow the official instructions on how to add poetry to your path if it is not already there. You can check this by running the following command line:

```bash
poetry --version
```  

## Project structure

Now that we have our development environment ready, we can start our project. For this, we need to create a new directory where our project will live. We will call this directory `flama_demo` for simplicity, but feel free to use any name you prefer. The following command line will create the directory and move you into it, and will initialise a new **poetry** project:

```bash
mkdir flama_demo \
  && cd flama_demo \
  && poetry init --python="~=3.11.5" --no-interaction \
  && touch README.md \
  && mkdir src
```

This will create a `pyproject.toml` file with the following information:

```toml
[tool.poetry]
name = "flama-demo"
version = "0.1.0"
description = ""
authors = ["YOUR USERNAME <your.user@email.com>"]
readme = "README.md"

[tool.poetry.dependencies]
python = "~=3.11.5"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
```

Inspecting the folder `flama_demo` you should see the following structure:

```bash
.
├── README.md
├── pyproject.toml
└── src
```

With this, we have created a new **poetry** project with the name `flama-demo`, which depends on Python version `3.11.5`. We have also created a `README.md` file, which is a good practice to document your project. Finally, we have created a `src` folder, which is where we will put the source code of our project.

## Installing dependencies

### Installing flama

Now that we have set up our project folder, we can proceed and add the dependencies of our project. We will start by adding `flama` as a dependency of our project. However, and before we do so, we need to know more about the extras that `flama` provides. Indeed, when you install `flama` you are installing the core functionality of the library, but there are some extra dependencies that you might need depending on the type of functionality you want to expose via your API. For example, `flama` provides support for the following typed data schemas:

- [Pydantic](https://pydantic-docs.helpmanual.io/): A library for data validation and settings management with support for type hints.
- [Typesystem](https://typesystem.readthedocs.io/en/latest/): A comprehensive library for data validation typically used to define typed data schemas which provides data validation and object serialization & deserialization tools.
- [Marshmallow](https://marshmallow.readthedocs.io/en/stable/): A library for data validation and serialization/deserialization.

Besides, `flama` also provides support for SQL databases via [SQLAlchemy](https://www.sqlalchemy.org/), an SQL toolkit and Object Relational Mapper that gives application developers the full power and flexibility of SQL. Finally, `flama` also provides support for HTTP clients to perform requests via [httpx](https://www.python-httpx.org/), a next generation HTTP client for Python.

These extras (you can check them [here](https://github.com/vortico/flama/blob/96d11508bacecb892547be56ea13d0dc565c4665/pyproject.toml#L49)) are not installed by default when you install `flama`, but can be installed by specifying them as extras. In our current example, we will install `flama` with support for all the extras, so we will run the following command line:

```bash
poetry add "flama[full]"
```

which will add the following lines to our `pyproject.toml` file:

```toml
[tool.poetry.dependencies]
python = "~=3.11.5"
flama = {extras = ["full"], version = "^1.6.0"}
```

To learn more about the different extras contained in `flama`, and how to pick up only those you need for a cleaner installation, you can check the [documentation]( https://flama.dev/docs/getting-started/installation#extras).

### Extra dependencies for ML

In addition to the dependencies that `flama` provides, we will also need to install some extra dependencies for our project. In particular, we will use:

- [scikit-learn](https://scikit-learn.org/stable/): A library for machine learning in Python
- [numpy](https://numpy.org/): A library for scientific computing in Python
- [pandas](https://pandas.pydata.org/): A library for data analysis in Python
- [pyarrow](https://arrow.apache.org/docs/python/): A library for efficient data interchange between Python and other languages

We can install these dependencies by running the following command line:

```bash
poetry add scikit-learn numpy pandas pyarrow
```

With this, we should have something like this in our `pyproject.toml` file:

```toml
[tool.poetry.dependencies]
python = "~=3.11.5"
flama = {extras = ["full"], version = "^1.6.0"}
scikit-learn = "^1.3.2"
numpy = "^1.26.2"
pandas = "^2.1.4"
pyarrow = "^14.0.1"
```

You don't need to worry if your `pyproject.toml` shows different versions for the dependencies, since this is exactly what **poetry** is for: to find the correct versions of the dependencies at the time of installation (which might be different from the ones shown here) and keep track of them for you.

With the needed dependencies already added to our project, we can proceed and install them in the active virtual environment by running the following command line:

```bash
poetry install
```

You can check everything is correctly installed by running:

```bash
poetry run flama --version
Flama 1.6.0
```

In the following, we are going to assume you have the environment correctly set up, hence it is up to you to run commands in the active virtual environment via `poetry run`, or simply activate the virtual environment and run the commands directly. E.g., in case you want to run the `flama` command line, you can do it via activating the virtual environment with `poetry shell` and then simply running the command line:

```bash
flama --version
```


## ML pipeline with scikit-learn

Since the main goal of this post is to showcase how to serve an ML model via an API (which we'll call ML-API) with `flama`, we need an ML model to be served, indeed. We could use any ML model developed with any of the main ML libraries in Python:

- [scikit-learn](https://scikit-learn.org/stable/)
- [TensorFlow](https://www.tensorflow.org/)
- [PyTorch](https://pytorch.org/)

However, we think it is a much better idea to quickly develop a simple ML model from scratch, showing how to build robust ML pipelines which not only contain the ML model itself, but also the pre-processing steps much needed later on when we want to make predictions with the model inside the ML-API. Failing in doing so is one of the most common mistakes when building ML-APIs, and typically leads to a lot of headaches when trying to deploy the ML model in production. Why? (you might ask). Well, because the ML model is typically trained after certain cleaning and transformation steps which ensure the data is *digestible* by the ML model. Thus, if we only package the ML model (typically yielding a [pickle file](https://docs.python.org/3/library/pickle.html)) without the pre-processing steps, when we try to make predictions with the model (by loading the corresponding artifact) we would end up with errors, since the data we want to use for making predictions is not in the same format as the data used for training the model. As you can already see, this is a reproducibility nightmare, and we want to avoid it at all costs.

Fortunately, the main ML libraries in Python provide tools to build ML pipelines to avoid this problem. In this post, we are going to use **scikit-learn** to build the pipeline we want to serve via our ML-API, but you can use any other library you prefer. 

### The data

The goal of this post is not to build a very complex ML model by itself, but we want to go further than the prototypical [Iris classification problem](https://scikit-learn.org/stable/auto_examples/datasets/plot_iris_dataset.html). For this reason, we are going to use a dataset which is a bit more complex, but still simple enough to be able to focus on the ML pipeline and the ML-API. The problem we are going to address has to do with the prediction of *customer churn*, i.e. the prediction of whether a customer will leave a company or not, which is a very common problem in the industry. The dataset we are going to use is a *public dataset*, which you can download from [here](https://github.com/vortico/flama-demo/blob/master/data/data.parquet). For the sake of brevity, we are not going to discuss here the details of the dataset, we will just assume that the data exploration has already been done.

Before we proceed with the ML pipeline, we are going to prepare the repository for the data and the ML pipeline script. To do so, we can run the following command lines:

```bash
mkdir -p data
mkdir -p src/pipeline
touch src/pipeline/__main__.py
```

And, later:

```bash
wget https://github.com/vortico/flama-demo/raw/master/data/data.parquet -O data/data.parquet
wget https://github.com/vortico/flama-demo/raw/master/data/artifact.json -O data/artifact.json
wget https://github.com/vortico/flama-demo/raw/master/data/input.json -O data/input.json
```

The project folder should look like this:

```bash
.
├── README.md
├── data
│   ├── artifact.json
│   ├── data.parquet
│   └── input.json
├── poetry.lock
├── pyproject.toml
└── src
    └── pipeline
        └── __main__.py
```

### The ML pipeline

Having all the data in place, we can proceed and build the ML pipeline. As we mentioned before, the aim of the post is not the building and training a perfect ML pipeline. Instead, we want to focus our attention on how to structure the pipeline, and the project, with the ultimate goal of packaging the pipeline and serving it via an ML-API. For this reason, we are going to build a very simple ML pipeline, which will consist of the following steps:

- **Data loading**: We will load the data from the `data.parquet` file into a `pandas.DataFrame` object.
- **Train-test split**: We will split the data into training and test sets.
- **Preprocessing numerical and categorical features**: We will apply some simple transformations to the numerical and categorical features of the dataset.
- **Training**: We will train a simple ML model using the training data.
- **Evaluation**: We will evaluate the performance of the model using the test data.

The code for this goes in the `src/pipeline/__main__.py` file, and it looks like this:

```python
import numpy as np
import pandas as pd

from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import roc_auc_score, f1_score

# Set random seed for reproducibility:
np.random.seed(123_456)

# Loading data:
dataset = pd.read_parquet("data/data.parquet")

X = dataset.drop(columns=["Exited"]).values

y = dataset["Exited"].values

columns = dataset.columns

# Preprocessing numerical features:
numeric_transformer = Pipeline(
    [
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
    ]
)
numeric_features = [
    columns.get_loc(c)
    for c in dataset.select_dtypes(include=["int64", "float64"])
    .drop(["RowNumber", "CustomerId", "Exited"], axis=1)
    .columns.values
]

# Preprocessing categorical features:
categorical_transformer = Pipeline(
    [
        ("imputer", SimpleImputer(strategy="constant", fill_value="missing")),
        ("onehot", OneHotEncoder(handle_unknown="ignore")),
    ]
)
categorical_features = [
    columns.get_loc(c)
    for c in dataset.select_dtypes(include=["object"])
    .drop(["Surname"], axis=1)
    .columns.values
]

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25)
preprocessor = ColumnTransformer(
    [
        ("numerical", numeric_transformer, numeric_features),
        ("categorical", categorical_transformer, categorical_features),
    ]
)

# Model train:
mlp = MLPClassifier(
    hidden_layer_sizes=(8, 6, 1),
    max_iter=300,
    activation="tanh",
    solver="adam",
    random_state=123_456,
)
pipeline = Pipeline(
    [
        ("preprocessing", preprocessor),
        ("mlp_classifier", mlp),
    ]
)
pipeline.fit(X_train, y_train)

# Model evaluation:
pipeline.score(X_test, y_test)
pipeline.predict(X_test)

print(f"""
Model trained successfully:
    * Accuracy: {pipeline.score(X_test, y_test)}
    * Predictions: {pipeline.predict(X_test)}
""")
```

You can run this script by simply running the following command line:

```bash
python -m src.pipeline

Model trained successfully:
    * Accuracy: 0.848
    * Predictions: [0 1 0 ... 0 0 0]
```

As you can see, the script trains a simple MLP classifier with 3 hidden layers, and it evaluates the performance of the model using the test data. The accuracy of the model is not great, but that's beyond the scope of this post. The important thing here is that we have a simple ML pipeline which we can use to make predictions when new data comes in, and we have tested it by evaluating the performance of the model with the test data.

## Packaging the ML pipeline: FLM files

### Why packing ML pipelines and models?

Before we proceed, it is worth discussing why we need to pack ML pipelines and models in the first place. There are several reasons for this, but we will focus on the following ones:

- **Persistence**: The ability to persist ML pipelines and models allows us to reuse them, either for further training, or for making predictions on new data.
- **Efficiency**: Binary files are compact, efficient, and easy way to store pipelines and models.
- **Portability**: Having ML pipelines self-contained in a single file allows us to transfer and use them across different environments.

### How to pack ML pipelines?

Let us assume we are where we are after careful experimentation, cross-validation, testing, and so on, and we have found the optimal ML model for our problem. Great job! 

Now, we want to take our model out of our Jupyter Notebook, or Python script, and offer it as a service to make predictions on demand. The first thing we think about is [pickling](https://docs.python.org/3/library/pickle.html#:~:text=%E2%80%9CPickling%E2%80%9D%20is%20the%20process%20whereby,back%20into%20an%20object%20hierarchy) (i.e., using `pickle.dump`) the model, and pass the resulting file to the corresponding team (or colleague) to develop the wrapper API which will have to eventually unpickle (i.e., using `pickle.load`) the object, and expose the `predict` method. It seems like a very repetitive and boring task, doesn't it?

**Flama** comes equipped with a very convenient CLI which does all the boring part for you seamlessly, just with a single line of code. For this, we only need our models to be packaged with the **Flama** counterparts of pickle's *dump* and *load* commands, namely: `flama.dump` and `flama.load`.

### Dumping the ML pipeline

**Flama**'s `dump` method uses optimal compression with the aim of making the packing process more efficient, and faster. In our case, we can dump the ML pipeline prepared before by adding the following lines to the `src/pipeline/__main__.py` file:

```python
# Add these new imports:
import flama

import datetime
import uuid

from sklearn.metrics import roc_auc_score, f1_score

# Here the script continues as before...

# Model dump:
id_ = uuid.UUID("e9d4a470-1eb2-423e-8fb3-eaf236158ab3")
path_ = "data/model.flm"
flama.dump(
    pipeline,
    path_,
    model_id=id_,
    timestamp=datetime.datetime.now(),
    params={"solver": "adam", "random_state": 123_456, "max_iter": 300},
    metrics={
        "accuracy": pipeline.score(X_test, y_test),
        "roc_auc_score": roc_auc_score(y_test, pipeline.predict(X_test)),
        "f1_score": f1_score(y_test, pipeline.predict(X_test)),
    },
    extra={
        "model_author": "Vortico",
        "model_description": "Churn classifier",
        "model_version": "1.0.0",
        "tags": ["loss", "churn"],
    },
    artifacts={"artifact.json": "./data/artifact.json"},
)

print(f"""
Model saved successfully:
    * File: {path_}
    * Id: {id_}
""")
```

The first two parameters are the ML pipeline object itself, and the path where the resulting file will be stored, respectively. The remaining parameters are optional, and are used to add metadata to the resulting file which might be quite useful for model management purposes. For further details on the use of these parameters, you can check the official [documentation](https://flama.dev/docs/machine-learning-api/packaging-models/).

At this point, if you run the script again, you should see a new file in the `data` folder called `model.flm`. This is the file we will use later on to serve the ML pipeline via an ML-API. Indeed, the running of the script should produce the following output:

```bash
python -m src.pipeline

Model trained successfully:
    * Accuracy: 0.848
    * Predictions: [0 1 0 ... 0 0 0]

Model saved successfully:
    * File: data/model.flm
    * Id: e9d4a470-1eb2-423e-8fb3-eaf236158ab3
```

### FLM files

OK, so we have the ML pipeline packaged as an FLM file, but what's that? FLM stands for *Flama Lightweight Model*. This comes from the fact that, FLM files are a lightweight representation of ML models, which come with useful metadata needed for later purposes, e.g. building a wrapper Flama API containing the model. To know more about FLM files, you can check the official [documentation](https://flama.dev/docs/machine-learning-api/packaging-models/#flm-files).

The structure of an FLM file is thought to be as simple as possible, and aims at keeping in a single file all the information needed to load and use the model. The structure of an FLM file is as follows:

```bash
├── model.flm
│   └── model
│       ├── model (python object)
│       └── meta
│           ├── id
│           ├── timestamp
│           ├── framework
│           ├── model
│           │   ├── obj
│           │   ├── info
│           │   ├── params
│           │   └── metrics
│           └── extra
└── artifacts
    ├── foo.json
    └── bar.csv
```

As you can see, the FLM file contains a wide range of information about the pipeline and model. 

### Loading the ML pipeline

We have an FLM file, and we would like to load it to make predictions, and so on. How can we do that? Well, we can use **Flama**'s `load` method, which is the counterpart of `dump`. In our case, we can load the ML pipeline by adding the following lines to the `src/pipeline/__main__.py` file:

```python
# Here the script continues as before...

# Load the ML pipeline:
pipeline = flama.load("./data/model.flm")
print(f"""
Model loaded successfully:
    * Id: {pipeline.meta.id}
    * Trained at: {pipeline.meta.timestamp}
    * Metrics: {pipeline.meta.model.metrics}
    * Author: {pipeline.meta.extra['model_author']}
""")
```

If you run the script again, you should see the following output:

```bash
python -m src.pipeline

Model trained successfully:
    * Accuracy: 0.848
    * Predictions: [0 1 0 ... 0 0 0]


Model saved successfully:
    * File: data/model.flm
    * Id: e9d4a470-1eb2-423e-8fb3-eaf236158ab3


Model loaded successfully:
    * Id: e9d4a470-1eb2-423e-8fb3-eaf236158ab3
    * Trained at: 2023-12-15 17:27:18.983044
    * Metrics: {'accuracy': 0.848, 'roc_auc_score': 0.7050107038056138, 'f1_score': 0.5571095571095571}
    * Author: Vortico
```

Hooray! 🥳🥳🥳 We have all the ingredients needed to build our ML API, and we have tested them to make sure everything works as expected. Now, we can proceed and see the magic of **Flama** in action.

## Serving the ML pipeline: Flama CLI

### The challenge

Once we have an ML pipeline trained and saved as a binary file, the process of serving the model usually requires addressing the following points:

- Develop a service wrapping the model
- Tackle the problem of the model lifecycle
- Define an interaction interface

This is a common pattern present in (almost) every ML project, and it lacks a standard to follow so far.

This challenge can materialise in two different ways:

- **Synchronous**: The client requests a prediction to the server and waits for the response. This can be solved with an HTTP service.

- **Asynchronous**: An event occurs and the server communicates the prediction to the client. This can be solved with a streaming service, or even with a websocket.

Good news? **Flama** brings all the tools needed to address both cases.

### The solution: Flama CLI

As we already saw at the very beginning of this post, **Flama** comes with the convenient `flama` command-line interface (CLI) at your disposal. Indeed, we already used it before when checking if all was correctly installed. In this section, we are going to deep dive a bit more into the CLI. For thi purpose, you only need to run the following command line:

```bash
flama --help

Usage: flama [OPTIONS] COMMAND [ARGS]...

  Fire up your models with Flama 🔥

Options:
  --version  Check the version of your locally installed Flama
  --help     Get help about how to use Flama CLI

Commands:
  model  Interact with an ML model without server.
  run    Run a Flama Application based on a route.
  serve  Serve an ML model file within a Flama Application.
  start  Start a Flama Application based on a config file.
```


### The `serve` command

The command serve comes to the rescue of those who are looking for an **instantaneous serving** of an ML model without having to write an app. This command, as we are about to see, only requires the file with the ML model to be served. The model will have to be saved as a binary file beforehand by using the tools offered by **Flama**, as we have just seen.

Without much further ado, let's see how to serve the model we have just trained and saved:

```bash
flama serve "data/model.flm"
INFO:     Started server process [64069]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

What just happened? As you can see we have a **Flama** application up and running on http://127.0.0.1 and listening the port `8000`. But, we have not written a single line of code! This is the **codeless approach of Flama to ML models deployment**, which makes possible the deployment of an already trained-and-tested ML model as an API ready to receive requests and return estimations almost without any effort, as you can see.

Before we proceed and make some requests to the ML-API, we can click on the link http://127.0.0.1:8000/ (or, simply, open it with your favourite browser) and check what is there waiting for us. You should see something like this:

```json
{"meta":{"id":"e9d4a470-1eb2-423e-8fb3-eaf236158ab3","timestamp":"2023-12-15T17:27:18.983044","framework":{"lib":"sklearn","version":"1.3.2"},"model":{"obj":"Pipeline","info":{"memory":null,"steps":[["preprocessing",null],["mlp_classifier",null]],"verbose":false,"preprocessing":null,"mlp_classifier":null,"preprocessing__n_jobs":null,"preprocessing__remainder":"drop","preprocessing__sparse_threshold":0.3,"preprocessing__transformer_weights":null,"preprocessing__transformers":[["numerical",null,[3,6,7,8,9,10,11,12]],["categorical",null,[4,5]]],"preprocessing__verbose":false,"preprocessing__verbose_feature_names_out":true,"preprocessing__numerical":null,"preprocessing__categorical":null,"preprocessing__numerical__memory":null,"preprocessing__numerical__steps":[["imputer",null],["scaler",null]],"preprocessing__numerical__verbose":false,"preprocessing__numerical__imputer":null,"preprocessing__numerical__scaler":null,"preprocessing__numerical__imputer__add_indicator":false,"preprocessing__numerical__imputer__copy":true,"preprocessing__numerical__imputer__fill_value":null,"preprocessing__numerical__imputer__keep_empty_features":false,"preprocessing__numerical__imputer__missing_values":null,"preprocessing__numerical__imputer__strategy":"median","preprocessing__numerical__scaler__copy":true,"preprocessing__numerical__scaler__with_mean":true,"preprocessing__numerical__scaler__with_std":true,"preprocessing__categorical__memory":null,"preprocessing__categorical__steps":[["imputer",null],["onehot",null]],"preprocessing__categorical__verbose":false,"preprocessing__categorical__imputer":null,"preprocessing__categorical__onehot":null,"preprocessing__categorical__imputer__add_indicator":false,"preprocessing__categorical__imputer__copy":true,"preprocessing__categorical__imputer__fill_value":"missing","preprocessing__categorical__imputer__keep_empty_features":false,"preprocessing__categorical__imputer__missing_values":null,"preprocessing__categorical__imputer__strategy":"constant","preprocessing__categorical__onehot__categories":"auto","preprocessing__categorical__onehot__drop":null,"preprocessing__categorical__onehot__dtype":null,"preprocessing__categorical__onehot__feature_name_combiner":"concat","preprocessing__categorical__onehot__handle_unknown":"ignore","preprocessing__categorical__onehot__max_categories":null,"preprocessing__categorical__onehot__min_frequency":null,"preprocessing__categorical__onehot__sparse":"deprecated","preprocessing__categorical__onehot__sparse_output":true,"mlp_classifier__activation":"tanh","mlp_classifier__alpha":0.0001,"mlp_classifier__batch_size":"auto","mlp_classifier__beta_1":0.9,"mlp_classifier__beta_2":0.999,"mlp_classifier__early_stopping":false,"mlp_classifier__epsilon":1e-08,"mlp_classifier__hidden_layer_sizes":[8,6,1],"mlp_classifier__learning_rate":"constant","mlp_classifier__learning_rate_init":0.001,"mlp_classifier__max_fun":15000,"mlp_classifier__max_iter":300,"mlp_classifier__momentum":0.9,"mlp_classifier__n_iter_no_change":10,"mlp_classifier__nesterovs_momentum":true,"mlp_classifier__power_t":0.5,"mlp_classifier__random_state":123456,"mlp_classifier__shuffle":true,"mlp_classifier__solver":"adam","mlp_classifier__tol":0.0001,"mlp_classifier__validation_fraction":0.1,"mlp_classifier__verbose":false,"mlp_classifier__warm_start":false},"params":{"solver":"adam","random_state":123456,"max_iter":300},"metrics":{"accuracy":0.848,"roc_auc_score":0.7050107038056138,"f1_score":0.5571095571095571}},"extra":{"model_author":"Vortico","model_description":"Churn classifier","model_version":"1.0.0","tags":["loss","churn"]}},"artifacts":{"artifact.json":"/var/folders/h4/vc_99fk53b93ttsv18ss8vhw0000gn/T/tmpomibzc6l/artifacts/artifact.json"}}
```

Indeed, we can get the same response by running the command line:

```bash
curl http://127.0.0.1:8000/

{"meta":{"id":"e9d4a470-1eb2-423e-8fb3-eaf236158ab3","timestamp":"2023-12-15T17:27:18.983044","framework":{"lib":"sklearn","version":"1.3.2"},"model":{"obj":"Pipeline","info":{"memory":null,"steps":[["preprocessing",null],["mlp_classifier",null]],"verbose":false,"preprocessing":null,"mlp_classifier":null,"preprocessing__n_jobs":null,"preprocessing__remainder":"drop","preprocessing__sparse_threshold":0.3,"preprocessing__transformer_weights":null,"preprocessing__transformers":[["numerical",null,[3,6,7,8,9,10,11,12]],["categorical",null,[4,5]]],"preprocessing__verbose":false,"preprocessing__verbose_feature_names_out":true,"preprocessing__numerical":null,"preprocessing__categorical":null,"preprocessing__numerical__memory":null,"preprocessing__numerical__steps":[["imputer",null],["scaler",null]],"preprocessing__numerical__verbose":false,"preprocessing__numerical__imputer":null,"preprocessing__numerical__scaler":null,"preprocessing__numerical__imputer__add_indicator":false,"preprocessing__numerical__imputer__copy":true,"preprocessing__numerical__imputer__fill_value":null,"preprocessing__numerical__imputer__keep_empty_features":false,"preprocessing__numerical__imputer__missing_values":null,"preprocessing__numerical__imputer__strategy":"median","preprocessing__numerical__scaler__copy":true,"preprocessing__numerical__scaler__with_mean":true,"preprocessing__numerical__scaler__with_std":true,"preprocessing__categorical__memory":null,"preprocessing__categorical__steps":[["imputer",null],["onehot",null]],"preprocessing__categorical__verbose":false,"preprocessing__categorical__imputer":null,"preprocessing__categorical__onehot":null,"preprocessing__categorical__imputer__add_indicator":false,"preprocessing__categorical__imputer__copy":true,"preprocessing__categorical__imputer__fill_value":"missing","preprocessing__categorical__imputer__keep_empty_features":false,"preprocessing__categorical__imputer__missing_values":null,"preprocessing__categorical__imputer__strategy":"constant","preprocessing__categorical__onehot__categories":"auto","preprocessing__categorical__onehot__drop":null,"preprocessing__categorical__onehot__dtype":null,"preprocessing__categorical__onehot__feature_name_combiner":"concat","preprocessing__categorical__onehot__handle_unknown":"ignore","preprocessing__categorical__onehot__max_categories":null,"preprocessing__categorical__onehot__min_frequency":null,"preprocessing__categorical__onehot__sparse":"deprecated","preprocessing__categorical__onehot__sparse_output":true,"mlp_classifier__activation":"tanh","mlp_classifier__alpha":0.0001,"mlp_classifier__batch_size":"auto","mlp_classifier__beta_1":0.9,"mlp_classifier__beta_2":0.999,"mlp_classifier__early_stopping":false,"mlp_classifier__epsilon":1e-08,"mlp_classifier__hidden_layer_sizes":[8,6,1],"mlp_classifier__learning_rate":"constant","mlp_classifier__learning_rate_init":0.001,"mlp_classifier__max_fun":15000,"mlp_classifier__max_iter":300,"mlp_classifier__momentum":0.9,"mlp_classifier__n_iter_no_change":10,"mlp_classifier__nesterovs_momentum":true,"mlp_classifier__power_t":0.5,"mlp_classifier__random_state":123456,"mlp_classifier__shuffle":true,"mlp_classifier__solver":"adam","mlp_classifier__tol":0.0001,"mlp_classifier__validation_fraction":0.1,"mlp_classifier__verbose":false,"mlp_classifier__warm_start":false},"params":{"solver":"adam","random_state":123456,"max_iter":300},"metrics":{"accuracy":0.848,"roc_auc_score":0.7050107038056138,"f1_score":0.5571095571095571}},"extra":{"model_author":"Vortico","model_description":"Churn classifier","model_version":"1.0.0","tags":["loss","churn"]}},"artifacts":{"artifact.json":"/var/folders/h4/vc_99fk53b93ttsv18ss8vhw0000gn/T/tmpomibzc6l/artifacts/artifact.json"}}
```

As you can see, the response is a JSON object containing all the information about the model, including the metadata we added when saving the model as an FLM file. This is very useful, since it allows us to check the model is the one we want to serve, and also to check the metadata of the model, which might be useful for model management purposes.

#### Auto documentation

Besides, the **serve** command also provides an interactive documentation of the ML-API which we can access and test by opening the following link in our browser: `http://127.0.0.1:8000/docs/`. You should see something like this:

![serve without params](.images/serve-no-params.png)

The documentation is automatically generated by **Flama** based on the information contained in the FLM file, and on the parameters passed to the `serve` command. The list of parameters accepted by the **serve** command  can be found in the [documentation](https://flama.dev/docs/flama-cli/serve/#parameters). In short, we can find the following groups of parameters:

- **Model parameters** 
  - `model-url`: Route of the model (default: `/`)
  - `model-name`: Name of the model (default: `model`)

- **App parameters**
  - `app-debug`: Enable debug mode (default: `False`)
  - `app-title`: Name of the application (default: `Flama`)
  - `app-version`: Version of the application (default: `0.1.0`)
  - `app-description`: Description of the application (default: `Fire up with the flame`)
  - `app-docs`: Description of the application (default: `Fire up with the flame`)
  - `app-schema`: Description of the application (default: `Fire up with the flame`)

  The parameter app-debug brings with it useful tools which make the debugging of the code easier, e.g. highly-detailed error messages, and interactive error webpages.

- **Server parameters**: All uvicorn options can be passed to the command serve with the format server-<UVICORN_OPTION_NAME>, as we discussed for the command run, e.g.:

  - `server-host`: Bind socket to this host (default: `127.0.0.1`)
  - `server-port`: Bind socket to this port (default: `8000`)

Knowing this, we can fine tune a bit our previous command line to make the automatically-generated documentation more appropriate for our ML-API:

```bash
flama serve "data/model.flm" \
  --app-title "Churn classifier" \
  --app-description "Predict whether a customer will leave a company or not" \
  --app-version "1.0.0"
```

which should produce the following output:

![Serve with parameters](.images/serve-with-params.png)

We encourage you to play around with the different parameters of the **serve** command to see how they work and help you customise the ML-API.

#### Making predictions

With the ML-API up and running, we can proceed and make some predictions. For this, we can use the **predict** endpoint, which is automatically generated by **Flama**. We can make predictions by sending a `POST` request to the endpoint `http://127.0.0.1:8000/predict/` (or, directly using the documentation of the `predict` endpoint). As an example, we can use the input data which we downloaded before under `data/input.json` as follows:

```bash 
curl --request POST \
  --url http://127.0.0.1:8000/predict/ \
  --header 'Accept: application/json' \
  --header 'Content-Type: application/json' \
  --data '{
  "input": [[10000, 15628319, "Walker", 792, "France", "Female", 28, 4, 130142.79, 1, 1, 0, 38190.78]]
}'

{"output":[0]}
```

or, with the documentation page:

![Model prediction with serve](.images/serve-model-predict.png)

As you can see, the response is a JSON object containing the prediction of the model. In this case, the model predicts the customer will not leave the company.

## Serverless interaction with the model

There is an alternative way to interact with the model stored as FLM file, which is by using the **model** command of the **Flama** CLI. This command allows us to interact with the model without having to start a server. Even though the main purpose of this post is to show how to serve an ML model via an API, we think it iws worth mentioning this alternative way of interacting with the model, since it might be useful in some cases. In any case, we plan to discuss this topic in a much more detailed way in future posts, so stay tuned for a more in-depth discussion on this. Also, you can check the official [documentation](https://flama.dev/docs/flama-cli/model/) if you want to deep dive by yourself in the meantime.

### The `model` command

In some cases, we want to interact with the model directly without the overhead of a server, e.g.:

- **Development & testing**: We are working with a model locally and want to try it out on some data to quickly see whether everything is working as expected. This is typically what happens when we're in the development stage of the ML lifecycle.

- **Streaming workflow**: This is also the case when we want to use a model as part of a larger pipeline where the model acts as a data processor in a stream of data, in which case we want to be able to pipe data into the model and get the output back.

The command `model` allows us to interact with models directly from the command line without the need for a server. To inspect the command options, run:

```bash
flama model --help

Usage: flama model [OPTIONS] FLAMA_MODEL_PATH COMMAND [ARGS]...

  Interact with an ML model without server.

  This command is used to directly interact with an ML model without the need
  of a server. This command can be used to perform any operation that is
  supported by the model, such as inspect, or predict. <FLAMA_MODEL_PATH> is
  the path of the model to be used, e.g. 'path/to/model.flm'. This can be
  passed directly as argument of the command line, or by environment variable.

Options:
  --help  Show this message and exit.

Commands:
  inspect  Inspect an ML model.
  predict  Make a prediction using an ML model.
```

We can check readily, by simply running:

```bash
flama model "data/model.flm" inspect
```

that the `inspect` subcommand gives us exactly the same information we got when we made a request to the root endpoint of the ML-API. 

Very likely, we are much more interested in the `predict` subcommand, which allows us to make predictions using the model. We can use an input file to be passed to the model, as we did manually before with the `/predict/` path of the ML-API. To do this, we only need to run:

```bash
flama model data/model.flm predict --file data/input.json --pretty

[
    0
]
```

The flag `--pretty` is used to print the output in a more human-readable way. The main advantage of this approach is that we can make predictions on a bunch of input data by simply passing the input file path. This is useful for local development and quick checks.

The previous command line is completely equivalent to the following one, which is more suitable for streaming services, or *pipe* several models together:

```bash
echo '[[10000, 15628319, "Walker", 792, "France", "Female", 28, 4, 130142.79, 1, 1, 0, 38190.78]]' | \
    flama model data/model.flm predict --pretty

[
    0
]
```

This, as just mentioned, is pretty useful if we want to chain several models, and make the output of one the output of the next in chain. E.g., imagine we have *n* models in files: `model_1.flm`, ..., `model_n.flm`, then we can pipe them as follows:

```bash
echo '[[<INPUT_DATA>]]' | \
    flama model model_1.flm predict | \
    flama model model_2.flm predict | \
    ...
    flama model model_n.flm predict
```


## Custom ML-APIs with Flama

So far, we have seen how to serve an ML pipeline with **Flama** CLI in a very simple way, without the need of writing a single line of code. This is a very powerful feature we cannot stress enough, not only because it allows to quickly have an ML-API up and running, but also (and more importantly) because it establishes a *standard of communication* between those who develop, train and test the ML pipeline; and those who have to put it into production. This is a very important point, since it allows to reduce the friction between the different teams involved in the ML lifecycle, and to make the process of putting ML pipelines into production much more efficient.

### Why custom ML APIs?

Despite all the good things we have seen so far, there are cases where the ML-API provided by the **Flama** CLI is not enough, and we need to develop a custom ML-API. This is the case, for instance, when we need:

- **Further functionality**: The ML-API provided by the **Flama** CLI comes with a set of endpoints which are enough for most cases. However, there might be some cases where we need to add further functionality to the ML-API, e.g. we might need to add a new endpoint to the ML-API to perform some specific task.
- **Fine control**: The ML-API provided by the **Flama** CLI is a "one size fits all" solution, which means that it is not possible to fine tune the behaviour of the ML-API. For instance, we might need to add some startup or shutdown events to the ML-API.
- **Learning by doing**: We might want to learn how to develop an ML-API from scratch, and **Flama** provides the perfect framework to do so.

### Flama Application

At the very beginning of this post we mentioned that **Flama** is a framework for the development of *lightweight applications*. Indeed, when we run the **serve** command before, a **Flama** application was created, equipped with the set of endpoints we saw before (i.e., `/`, `/docs/`, `/schema/`, and `/predict/`), and run under the hood, without you ever noticing. Specifically: 

- `/` is the root endpoint of the ML-API, which returns the inspection of the model (as we saw before with `flama model inspect`).
- `/docs/` is the endpoint which provides the automatically-generated documentation of the ML-API.
- `/predict/` is the endpoint which allows us to make predictions using the corresponding `predict()` method of the ML pipeline. This endpoint is in charge of unpacking the FLM file, and calling the `predict()` method.

#### The base application

If we want to develop a custom ML-API, we need to start by creating a **Flama** application, and we will do so taking some inspiration from the official [documentation](https://flama.dev/docs/machine-learning-api/add-models/). For this, we will create a new folder called `src/api`:

```bash
mkdir src/api
```

and will add a new file called `src/api/app.py` with the following content:

```python
from flama import Flama

app = Flama(
    title="Flama ML",
    version="1.0.0",
    description="Machine learning API using Flama 🔥",
    docs="/docs/"
)

@app.get("/")
def home():
    """
    tags:
        - Home
    summary:
        Returns warming message
    description:
        The function returns a hello message
    """
    return "Hello 🔥"
```

And we can run the application by simply running:

```bash
flama run src.api.app:app

INFO:     Started server process [68609]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

To know more about the **run** command of the **Flama** CLI, please have a look at the [documentation](https://flama.dev/docs/flama-cli/run/).

If we want to run the application as a Python script, we can add the following lines to the file `src/api/__main__.py`:

```python
import flama

def main():
    flama.run(flama_app="src.api.app:app", server_host="0.0.0.0", server_port=8000, server_reload=True)

if __name__ == "__main__":
    main()
```

and run the application by simply running:

```bash
python -m src.api

INFO:     Will watch for changes in these directories: ['/<YOUR_PATH>/flama_demo']
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [70508] using StatReload
INFO:     Started server process [70512]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

Wonderful! 🥳🥳🥳 We have our **Flama** application up and running, with a custom endpoint which returns a warming message.
Now, we can proceed and add the ML pipeline we trained before to the application.

In case you did not notice, the fact that we used the parameter `server_reload=True` with `flama.run` in the `__main__.py` file activated the *hot reloading* feature of **Flama**, which means that the application will be reloaded every time we make a change to the code. This is very useful for development purposes, since it allows us to make changes to the code without having to restart the application every time.


#### Add the ML resource

Let us assume we want our ML-API to satisfy the following requirements:

1. The churn pipeline must be exposed under the route `/churn/`
2. We want to have exposed the `predict` method of the pipeline as we already had before
3. We want to have a new endpoint which returns the estimation of financial loss due to churn of a given customer (more details below).

For the first two requirements, we are going to use three built-in ingredients of **Flama** which we haven't seen yet, namely:

- `ModelResource`: This is a built-in class which derives from the most fundamental resource class `BaseResource`. These classes can be seen as the *interface* that any custom model class will need to adhere to. In case you're not familiar with the interface design pattern, it can be very succinctly described as *a blueprint for designing classes*.

- `ModelResourceType`: This is a built-in [metaclass](https://docs.python.org/3/reference/datamodel.html?highlight=metaclass#metaclasses) which derives from the most fundamental resource type metaclass `ResourceType`. The concept of metaclass is a bit less intuitive, and some highly recognised *pythonists* recommend to avoid them at all costs. We agree with such a claim, which is why you won't need to worry about them, apart from having to import the ModelResourceType, and use it as an argument when building your custom model class.

- `resource_method` decorator: This is a built-in [decorator](https://docs.python.org/3/glossary.html#term-decorator) which allows us to convert a given class method into an app endpoint, with the following main arguments:

  - `path`: Route path through which we'll be able to call the decorated method, e.g. `/predict/`
  - `methods`: HTTP methods associated with the endpoint, e.g. `GET` or `POST`
  - `name`: Name which uniquely determines the route being added to the app.


Let's add the ML pipeline to the application by adding the following lines to the file `src/api/app.py`:

```python
# Add these imports:
from flama.models import ModelResource, ModelResourceType

# Here the script continues as before...

# Add the ML pipeline:

class ChurnModel(ModelResource, metaclass=ModelResourceType):
    name = "churn_model"
    verbose_name = "Churn model"
    model_path = "data/model.flm"

app.models.add_model_resource(path="/churn", resource=ChurnModel)
```

As you can see, we have created a new class called `ChurnModel` which derives from `ModelResource`, and we have added it to the application by using the `add_model_resource` method of the `models` attribute of the application. This method can take several arguments, but we are mostly interested in the following ones:

- `path`: Route path where the method **predict** will be placed, e.g. `path="/churn/"` means that the method **predict** will be placed under the route `/churn/predict/`.
- `resource`: Resource class to be added to the application.

Given that the class `ChurnModel` inherits from `ModelResource` and uses `ModelResourceType` as metaclass, it will have the following methods:

- `/`: Returns the inspection of the model.
- `/predict/`: Returns the prediction of the model.

We can check this by running the application again:

```bash
flama run src.api.app:app
```

or 

```bash
python -m src.api
```

and opening the documentation page at `http://127.0.0.1:8000/docs/`.

With the previous code, we are already serving the ML pipeline as we wanted, and satisfying the requirements (1) and (2).
What about the custom endpoint we wanted to add?

#### Add a custom endpoint to the Churn model resource
 
It seems we have everything almost ready to just add the custom endpoint we were told to add. Let us imagine our data-science colleague has developed a formula to estimate the financial loss due to the churn of a given customer, which looks like:

{% katex %} \text{loss}[\$] = \mathbb{P}[\{\text{churn}\}] \times \left(N \times \text{Income}[\$] - \text{OPEX}[\$]\right) {% endkatex %}

where:

- `Average annal income`: Estimated average annual income of the customer
- `Churn probability`: Probability of churn of the customer which we get from the ML pipeline (i.e., the output of the `predict` method).
- `Agents per client`: Number of agents assigned to the customer
- `Operational cost`: Operational cost of the company

Out of the four parameters of the formula, we only have the first two: the estimated annual income of the customer (which will be passed as the ninth element of the input data), and the churn probability (which we get from the `predict` method of the ML pipeline). The other two parameters are not part of the input, but are parameters which were known/computed during the training stage, and were stored together with the ML pipeline as part of the FLM file, under the `artifacts` attribute of the `dump` method of the pipeline (see, `artifacts={"artifact.json": "./data/artifact.json"}`). This is very useful, since it allows us to use such information which was computed during the training stage, and use it in the production stage without having to recompute it again, or having to introduce it manually in the code of the ML-API (typically as constants, or in a configuration file).

We can add the custom endpoint to the `ChurnModel` class by adding the following lines to the file `src/api/app.py`:

```python
# Add these imports:
import json

import numpy as np

from flama import schemas, types
from flama.models import ModelResource, ModelResourceType
from flama.resources import resource_method

# Here the script continues as before...

# Add the ML pipeline:
class ChurnModel(ModelResource, metaclass=ModelResourceType):
    name = "churn_model"
    verbose_name = "Churn model"
    model_path = "data/model.flm"

    @resource_method("/loss/", methods=["POST"], name="model-predict-loss")
    def predict_loss(
        self, data: types.Schema[schemas.schemas.MLModelInput]
    ) -> types.Schema[schemas.schemas.MLModelOutput]:
        """
        tags:
            - Churn model
        summary:
            Get loss from churn
        description:
            Computes the loss amount estimated according to the model parameters
            provided in the model artifacts, with loss being the product of the
            churn probability and the estimated salary of the client minus the
            operational cost of the company.
        """
        with open(self.model.artifacts["artifact.json"]) as f:
            params = json.load(f)

        x = np.array(data["input"])
        proba = self.model.model.predict_proba(x)[:, 0]

        loss = proba * (
            params["agents_per_client"] * x[:, 8].astype(float) - params["operational_cost"]
        )
        return types.Schema[schemas.schemas.MLModelOutput]({"output": loss.tolist()})

app.models.add_model_resource(path="/churn", resource=ChurnModel)
```

After adding the new code to the application source file, **Flama** will reload the application automatically, and you should see the new endpoint `/churn/loss/` in the documentation page. To test it, you can either use the documentation page, or run the following command line:

```bash
curl --request POST \
  --url http://127.0.0.1:8000/churn/loss/ \
  --header 'Accept: application/json' \
  --header 'Content-Type: application/json' \
  --data '{
  "input": [[10000, 15628319, "Walker", 792, "France", "Female", 28, 4, 130142.79, 1, 1, 0, 38190.78]]
}'

{"output":[5212.2945950392195]}%
```

Great news! 🥳🥳🥳 We have successfully added a custom endpoint to the ML-API, and we have tested it to make sure it works as expected. In this case, we have an estimated loss of `$5212.29` due to the churn of the customer.


## Conclusions

In this post we have seen how to build and serve a robust ML pipeline with **Flama**. We have seen how to train and save an ML pipeline, and how to serve it as an API with the **Flama** CLI. We have also seen how to interact with the model without the need of a server, and how to develop a custom ML-API with **Flama**. Finally, we have also shown how to add custom endpoints to the ML-API, and how to use the information stored in FLM files, e.g. to compute the output of a custom endpoint. 

We certainly believe that **Flama** is a very powerful tool which can help you to put your ML pipelines into production in a very efficient way. We encourage you to try it out, and to give us feedback on how to improve it. We are looking forward to hearing from you! 🤗

Finally, we would like to thank you for reading this post, and we hope you enjoyed it. If you have any questions, please do not hesitate to contact us. We will be more than happy to help you! 🤓

## References

- [Flama documentation](https://flama.dev/docs/)
- [Flama GitHub repository](https://github.com/vortico/flama)
- [Flama PyPI package](https://pypi.org/project/flama/)

## About the authors

- [Vortico](https://vortico.tech/): We are specialised in software development to helps businesses enhance and expand their AI and technology capabilities.
