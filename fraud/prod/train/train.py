# %%
#! pip install kaggle --upgrade
#! kaggle --version
#! kaggle competitions download -c ieee-fraud-detection --force
# %%

if __name__ == "__main__":

    import pandas as pd
    import numpy as np
    import os

    import sklearn.preprocessing as sk_prep
    from sklearn.model_selection import train_test_split
    import xgboost as xgb
    import joblib

    from sklearn.metrics import accuracy_score, recall_score, roc_auc_score, precision_score
    ######

    prod = True # boolean for production vs testing differences
    laptop = False #boolean for running on my laptop lol

    train = pd.DataFrame()

    if laptop:
        import zipfile
        zf = zipfile.ZipFile("C:\\Users\\Ben\\Documents\\YC\\mygit\\BenZuckier\\DSA\\06_Fraud_Model\\ieee-fraud-detection.zip")
        train = pd.read_csv(zf.open('train_transaction.csv'))
        del zf
    else:
        train = pd.read_csv('/content/train_transaction.csv.zip', compression='zip')
    # valid = pd.read_csv('/content/test_transaction.csv.zip', compression='zip')

    train = train.drop("TransactionID", axis=1)

    # lets remove V cols except v307 and v310 which perfromed well in testing
    v310 = train[["V310"]].copy()
    v307 = train[["V307"]].copy()
    train = train.loc[:,~train.columns.str.startswith('V')]
    train["V310"] = v310[["V310"]]
    train["V307"] = v307[["V307"]]

    # engineer two new features
    train['TimeInDay'] = train.TransactionDT % 86400
    train['Cents'] = train.TransactionAmt % 1

    # rename the cols we're gonna onehot
    # train = train.rename(columns={'card4':'card4d', 'card6':'card6f', 'P_emaildomain': 'pEmail','R_emaildomain':'rEmail', 'M1':'M1a', 'M2':'M2b', 'M3':'M3c', 'M4':'M4d', 'M5':'M5e', 'M6':'M6f', 'M7':'M7g', 'M8':'M8h', 'M9':'M9i'})

    # shplits
    train_txn, test_txn = train_test_split(train, test_size=0.25, stratify=train[['isFraud']])
    del train

    y_train = train_txn["isFraud"].copy()
    X_train = train_txn.drop("isFraud", axis=1)
    del train_txn

    y_test = test_txn['isFraud'].copy()
    X_test = test_txn.drop('isFraud',axis=1)
    del test_txn

    # y_valid = valid["isFraud"].copy()
    # X_valid = valid.drop("isFraud",axis=1).copy()
    # del valid

    # Label Encode any non numeric col
    toLabel = [f for f in X_train.columns if X_train[f].dtype=='object']

    onehot = sk_prep.OneHotEncoder(handle_unknown='ignore',sparse=False)
    onehot.fit(X_train[toLabel])
    onehotted = onehot.transform(X_train[toLabel])
    # pd.DataFrame(onehotted)
    col_names = onehot.get_feature_names(toLabel)
    onehotDat =  pd.DataFrame(onehotted, columns= col_names, index=X_train.index)
    X_train = pd.concat([X_train.drop(toLabel,axis=1), onehotDat], axis=1 )

    # # robust scaler our numerical data cols
    # robust = sk_prep.RobustScaler().fit(X_train[["TransactionAmt"]])
    # pd.options.mode.chained_assignment = None
    # train[['cdev','trainhr']] = robust.transform(train[['cdev','trainhr']])
    # pd.options.mode.chained_assignment = 'warn'

    clf = xgb.XGBClassifier(
        n_estimators=500,
        max_depth=9,
        learning_rate=0.05,
        subsample=0.9,
        colsample_bytree=0.9,
        random_state=69,
        tree_method='gpu_hist' # set runtime to gpu to take advantage
    )
    model = clf.fit(X_train, y_train, eval_metric="auc")

    folder = './models'
    try:
        os.makedirs(folder)
    except FileExistsError:
        pass

    for x in [(onehot,"onehot"),(toLabel,"labelCols"),(col_names,"onehottedLabels"),(model,"xgb")]:
        (mod,nom) = x
        with open(os.path.join(folder,nom), "wb") as f:
                joblib.dump(mod, f)


    if not prod:
        X_test_enc = X_test.copy()
        onehotted_test = onehot.transform(X_test_enc[toLabel])
        # pd.DataFrame(onehotted)
        # col_names = onehot.get_feature_names(toLabel)
        onehotDat_test =  pd.DataFrame(onehotted_test, columns=col_names, index=X_test_enc.index)
        X_test_enc = pd.concat([X_test_enc.drop(toLabel, axis=1), onehotDat_test], axis=1)

        pred = model.predict(X_test_enc)
        pred_proba = model.predict_proba(X_test_enc)
        xgb_df = pd.DataFrame(data=[accuracy_score(y_test, pred), recall_score(y_test, pred),
                        precision_score(y_test, pred), roc_auc_score(y_test, pred_proba[:,1])], 
                    columns=['XGB Score'],
                    index=["Accuracy", "Recall", "Precision", "ROC AUC Score"])
        display(xgb_df)

    print("done")

# %%
