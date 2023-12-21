import json

import numpy as np

from flama import Flama
from flama import schemas, types
from flama.models import ModelResource, ModelResourceType
from flama.resources import resource_method

app = Flama(
    title="Flama ML",
    version="1.0.0",
    description="Machine learning API using Flama 🔥",
    docs="/docs/",
)


@app.route("/", methods=["GET"])
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
