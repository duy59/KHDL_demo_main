import pandas as pd
from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import fpgrowth, association_rules
import json
import time

def save_results_to_json(freqItems, rules, output_file, min_support_ratio=0.005, min_confidence=0.5):
    """
    Lưu kết quả vào file JSON theo định dạng giống code thuần.
    """
    # Chuyển đổi tập hợp thành danh sách để có thể lưu vào JSON
    freq_items_json = [list(itemset) for itemset in freqItems]

    rules_json = []
    for _, row in rules.iterrows():
        rules_json.append({
            "antecedent": list(row['antecedents']),
            "consequent": list(row['consequents']),
            "confidence": row['confidence']
        })

    result = {
        "metadata": {
            "min_support_ratio": min_support_ratio,
            "min_confidence": min_confidence,
            "total_frequent_itemsets": len(freqItems),
            "total_rules": len(rules_json)
        },
        "frequent_itemsets": freq_items_json,
        "association_rules": rules_json
    }

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=4, ensure_ascii=False)

    print(f"✔️ Đã lưu kết quả JSON vào: {output_file}")


def run_library_algorithm(transactions_list, min_support_ratio, min_confidence):
    """
    Chạy thuật toán FP-Growth bằng thư viện mlxtend

    Args:
        transactions_list: List of transactions (list of lists)
        min_support_ratio: Support threshold
        min_confidence: Confidence threshold

    Returns:
        dict: Kết quả với frequent_itemsets, association_rules, execution_time
    """
    print(f"\n{'='*60}")
    print(f"LIBRARY ALGORITHM (MLXTEND) - EXECUTION")
    print(f"{'='*60}")
    print(f"📚 Using mlxtend library")
    print(f"⚙️ Support threshold: {min_support_ratio}")
    print(f"⚙️ Confidence threshold: {min_confidence}")
    print(f"📊 Total transactions: {len(transactions_list)}")

    start_time = time.time()

    try:
        # One-hot encoding
        print("🔄 Performing one-hot encoding...")
        te = TransactionEncoder()
        te_ary = te.fit(transactions_list).transform(transactions_list)
        df_encoded = pd.DataFrame(te_ary, columns=te.columns_)
        print(f"✅ Encoded {len(df_encoded)} transactions with {len(te.columns_)} unique items")

        # Tìm tập mục phổ biến
        print("⛏️ Mining frequent itemsets...")
        frequent_itemsets = fpgrowth(df_encoded, min_support=min_support_ratio, use_colnames=True)
        print(f"✅ Found {len(frequent_itemsets)} frequent itemsets")

        # Sinh luật kết hợp
        print("🔗 Generating association rules...")
        if len(frequent_itemsets) > 0:
            rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=min_confidence)
            print(f"✅ Generated {len(rules)} association rules")
        else:
            rules = pd.DataFrame()
            print("❌ No frequent itemsets found, cannot generate rules")

        end_time = time.time()
        execution_time = end_time - start_time

        # Format kết quả
        formatted_itemsets = []
        for _, row in frequent_itemsets.iterrows():
            formatted_itemsets.append({
                'itemset': list(row['itemsets']),
                'support': round(row['support'], 4)
            })

        # Sắp xếp itemsets theo support giảm dần
        formatted_itemsets.sort(key=lambda x: x['support'], reverse=True)

        # Thêm số thứ tự
        for i, itemset in enumerate(formatted_itemsets, 1):
            itemset['rank'] = i

        formatted_rules = []
        for _, row in rules.iterrows():
            formatted_rules.append({
                'antecedent': list(row['antecedents']),
                'consequent': list(row['consequents']),
                'confidence': round(row['confidence'], 4),
                'support': round(row['support'], 4),
                'lift': round(row['lift'], 4)
            })

        # Sắp xếp theo confidence từ cao xuống thấp
        formatted_rules.sort(key=lambda x: x['confidence'], reverse=True)

        print(f"⏱️ Library execution time: {execution_time:.4f} seconds")
        print(f"✅ Library algorithm completed successfully")

        return {
            'frequent_itemsets': formatted_itemsets,
            'association_rules': formatted_rules,
            'execution_time': execution_time,
            'algorithm': 'mlxtend_fpgrowth',
            'parameters': {
                'support_threshold': min_support_ratio,
                'confidence_threshold': min_confidence
            }
        }

    except Exception as e:
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"❌ Library algorithm failed: {str(e)}")
        return {
            'error': str(e),
            'execution_time': execution_time,
            'algorithm': 'mlxtend_fpgrowth'
        }

def main():
    # Đọc dữ liệu
    input_file = "invoice_summary.csv"
    print(f"Đọc dữ liệu từ {input_file}...")
    df = pd.read_csv(input_file)
    transactions = df["ListItem"].dropna().apply(lambda x: x.split(",")).tolist()

    # Cài đặt ngưỡng
    min_support_ratio = 0.005
    min_confidence = 0.5

    # Chạy thuật toán thư viện
    result = run_library_algorithm(transactions, min_support_ratio, min_confidence)

    # Xuất file JSON
    json_file = "fpgrowth_results_lib.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=4, ensure_ascii=False)
    print(f"✔️ Đã lưu kết quả JSON vào: {json_file}")


if __name__ == "__main__":
    main()
