import numpy as np

# compute base forecast no coherent
from mlforecast import MLForecast
from sklearn.tree import DecisionTreeRegressor

#obtain hierarchical reconciliation methods and evaluation
from hierarchicalforecast.core import HierarchicalReconciliation
from hierarchicalforecast.evaluation import HierarchicalEvaluation
from hierarchicalforecast.methods import MinTrace

# Hierarchical latency prediction
# Y_train_df & Y_test_df: latency series
# S: the summing matrix of the hierarchy
# tags: each key is a level and its value contains tags associated to that level
# horizon: the forecast horizon
def hierarchical_forecasting(Y_train_df, Y_test_df, S, tags, horizon):

    # Compute base predictions from regression trees
    fcml = MLForecast(
        models=[DecisionTreeRegressor()],
        lags=[1],
        freq=1 # we'll just add 1 in every time window
    )
    fcml.fit(Y_train_df)
    Y_hat_df = fcml.predict(horizon)

    # Reconcile the base predictions
    reconcilers = [
        MinTrace(method='mint_shrink')
    ]
    hrec = HierarchicalReconciliation(reconcilers=reconcilers)
    Y_rec_df = hrec.reconcile(Y_hat_df=Y_hat_df, Y_df=Y_train_df,
                              S=S, tags=tags)

    # Evaluate the forecasting results
    def mse(y, y_hat):
        return np.mean((y-y_hat)**2)

    evaluator = HierarchicalEvaluation(evaluators=[mse])
    evaluator.evaluate(Y_hat_df=Y_rec_df, Y_test_df=Y_test_df,
                       tags=tags, benchmark='Naive')