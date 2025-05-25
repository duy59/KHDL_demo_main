import pandas as pd
import os

def process_transaction(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    if ext == '.xlsx':
        df = pd.read_excel(file_path)
    elif ext == '.csv':
        df = pd.read_csv(file_path)
    else:
        raise ValueError("File phải là .csv hoặc .xlsx")

    df = df.dropna(subset=['CustomerID'])
    df = df[~df['InvoiceNo'].astype(str).str.startswith('C')]
    df = df[(df['Quantity'] > 0) & (df['UnitPrice'] > 0)]
    df = df[~df['StockCode'].isin(['POST', 'M'])]
    df = df.reset_index(drop=True)

    transactions_dict = (
        df.groupby('InvoiceNo')['StockCode']
        .apply(lambda x: list(set(str(code) for code in x)))
        .to_dict()
    )

    transactions = list(transactions_dict.values())

    return transactions


