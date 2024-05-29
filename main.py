import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
import recourse as rs

# import data
url = "https://raw.githubusercontent.com/ustunb/actionable-recourse/master/examples/paper/data/credit_processed.csv"
df = pd.read_csv(url)
y, X = df.iloc[:, 0], df.iloc[:, 1:]

# train a classifier
clf = LogisticRegression(max_iter=1000)
clf.fit(X, y)
yhat = clf.predict(X)

# customize the set of actions
## matrix of features. ActionSet will set bounds and step sizes by default
A = rs.ActionSet(X)

# specify immutable variables
A["Married"].actionable = False

# can only specify properties for multiple variables using a list
A[["Age_lt_25", "Age_in_25_to_40", "Age_in_40_to_59", "Age_geq_60"]].actionable = False

# education level
A["EducationLevel"].step_direction = 1  ## force conditional immutability.
A["EducationLevel"].step_size = 1  ## set step-size to a custom value.
A["EducationLevel"].step_type = "absolute"  ## force conditional immutability.
A["EducationLevel"].bounds = (0, 3)

A["TotalMonthsOverdue"].step_size = 1  ## set step-size to a custom value.
## discretize on absolute values of feature rather than percentile values
A["TotalMonthsOverdue"].step_type = "absolute"
A["TotalMonthsOverdue"].bounds = (0, 100)  ## set bounds to a custom value.

## get model coefficients and align
## tells `ActionSet` which directions each feature should move in to produce positive change.
A.set_alignment(clf)

# Get one individual
i = np.flatnonzero(yhat <= 0).astype(int)[0]

# build a flipset for one individual
fs = rs.Flipset(x=X.values[i], action_set=A, clf=clf)
fs.populate(enumeration_type="distinct_subsets", total_items=10)
fs.to_latex()
fs.to_html()

# # Run Recourse Audit on Training Data
# auditor = rs.RecourseAuditor(A, coefficients=clf.coef_, intercept=clf.intercept_)
# audit_df = auditor.audit(X)  ## matrix of features over which we will perform the audit.

# ## print mean feasibility and cost of recourse
# print(audit_df["feasible"].mean())
# print(audit_df["cost"].mean())
# print_recourse_audit_report(X, audit_df, y)
# # or produce additional information of cost of recourse by other variables
# # print_recourse_audit_report(X, audit_df, y, group_by = ['y', 'Married', 'EducationLevel'])
