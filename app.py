from flask import Flask, render_template, request, jsonify
import pandas as pd
import os
import time
import tempfile
from werkzeug.utils import secure_filename
import json

# Import các module thuật toán
from clean_data import process_transaction
from apriori_test import main_apriori_algorithm, print_final_results
from fpgrowth_test import fpgrowth, printResults
from code_lib import run_library_algorithm

# Load product descriptions
def load_product_descriptions():
    """Load product descriptions from CSV file"""
    try:
        df = pd.read_csv('stockcode_description.csv')
        # Remove rows with NaN values and convert to string
        df = df.dropna()
        descriptions = {}
        for _, row in df.iterrows():
            stock_code = str(row['StockCode']).strip()
            description = str(row['Description']).strip()
            if stock_code and description:
                descriptions[stock_code] = description
        print(f"Loaded {len(descriptions)} product descriptions")
        return descriptions
    except Exception as e:
        print(f"Warning: Could not load product descriptions: {e}")
        return {}

# Global variables
PRODUCT_DESCRIPTIONS = load_product_descriptions()
LIBRARY_RESULTS = None  # Store library results for comparison

def get_product_name(stock_code):
    """Get product description from stock code"""
    return PRODUCT_DESCRIPTIONS.get(str(stock_code), f"Unknown Product ({stock_code})")

def format_rule_description(antecedent, consequent, confidence):
    """Format association rule with product names"""
    # Convert all items to string to handle mixed types
    antecedent = [str(item) for item in antecedent]
    consequent = [str(item) for item in consequent]

    if len(antecedent) == 1 and len(consequent) == 1:
        # Single item -> Single item
        antecedent_name = get_product_name(antecedent[0])
        consequent_name = get_product_name(consequent[0])
        return f"Nếu mua {antecedent_name} thì khả năng mua {consequent_name} với độ tin cậy là: {confidence*100:.1f}%"
    else:
        # Multiple items
        antecedent_names = [get_product_name(item) for item in antecedent]
        consequent_names = [get_product_name(item) for item in consequent]

        antecedent_text = " và ".join(antecedent_names)
        consequent_text = " và ".join(consequent_names)

        return f"Nếu mua {antecedent_text} thì khả năng mua {consequent_text} với độ tin cậy là: {confidence*100:.1f}%"

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size

ALLOWED_EXTENSIONS = {'csv', 'xlsx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def capture_algorithm_steps(algorithm_func, *args):
    """Capture algorithm execution steps and results"""
    import io
    import sys
    from contextlib import redirect_stdout

    # Capture stdout
    captured_output = io.StringIO()
    start_time = time.time()

    with redirect_stdout(captured_output):
        result = algorithm_func(*args)

    end_time = time.time()
    execution_time = end_time - start_time

    steps = captured_output.getvalue()
    return result, steps, execution_time

def format_transactions_for_algorithms(transactions_list):
    """Clean data already returns list format, just pass through with debug info"""
    print(f"Debug: transactions_list type: {type(transactions_list)}")
    print(f"Debug: transactions_list length: {len(transactions_list)}")
    print(f"Debug: transactions_list sample: {transactions_list[:3] if transactions_list else 'Empty'}")

    return transactions_list

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400

        file = request.files['file']
        algorithm = request.form.get('algorithm', 'apriori')
        support_threshold = float(request.form.get('support_threshold', 0.3))
        confidence_threshold = float(request.form.get('confidence_threshold', 0.6))

        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Please upload CSV or XLSX files.'}), 400

        # Save uploaded file temporarily
        filename = secure_filename(file.filename)
        temp_dir = tempfile.mkdtemp()
        temp_file_path = os.path.join(temp_dir, filename)
        file.save(temp_file_path)

        # Step 1: Clean data
        print("Processing data...")
        clean_start_time = time.time()
        transactions_list = process_transaction(temp_file_path)  # clean_data.py trả về list
        clean_end_time = time.time()
        clean_time = clean_end_time - clean_start_time

        # Format for algorithms (just pass through with debug)
        transactions_list = format_transactions_for_algorithms(transactions_list)

        # Debug: Check if we have enough data
        print(f"Debug: Total transactions after cleaning: {len(transactions_list)}")
        if len(transactions_list) == 0:
            return jsonify({'error': 'No valid transactions found after data cleaning'}), 400

        # Calculate minimum support count
        min_support_count = len(transactions_list) * support_threshold
        print(f"Debug: Minimum support count needed: {min_support_count} (threshold: {support_threshold})")

        # Show sample transactions
        print("Debug: Sample transactions:")
        for i, trans in enumerate(transactions_list[:5]):
            print(f"  Transaction {i+1}: {trans}")

        if len(transactions_list) < 5:
            print("Warning: Very few transactions. Consider lowering support threshold.")

        # Step 2: Run library algorithm in parallel
        print("Running library algorithm...")
        library_start_time = time.time()
        library_result = run_library_algorithm(transactions_list, support_threshold, confidence_threshold)
        library_end_time = time.time()
        library_time = library_end_time - library_start_time

        # Store library results globally for comparison
        global LIBRARY_RESULTS
        LIBRARY_RESULTS = library_result

        # Step 3: Run selected algorithm
        if algorithm == 'apriori':
            result, steps, exec_time = capture_algorithm_steps(
                main_apriori_algorithm,
                transactions_list,
                support_threshold,
                confidence_threshold
            )
            itemsets, rules = result

            # Format results for JSON
            formatted_itemsets = []
            for itemset, support in itemsets:
                formatted_itemsets.append({
                    'itemset': list(itemset),
                    'support': round(support, 4)
                })

            # Sắp xếp itemsets theo support giảm dần
            formatted_itemsets.sort(key=lambda x: x['support'], reverse=True)

            # Thêm số thứ tự
            for i, itemset in enumerate(formatted_itemsets, 1):
                itemset['rank'] = i

            formatted_rules = []
            for (antecedent, consequent), confidence in rules:
                formatted_rules.append({
                    'antecedent': list(antecedent),
                    'consequent': list(consequent),
                    'confidence': round(confidence, 4),
                    'description': format_rule_description(list(antecedent), list(consequent), confidence)
                })

            # Sắp xếp theo confidence từ cao xuống thấp
            formatted_rules.sort(key=lambda x: x['confidence'], reverse=True)

        else:  # fp-growth
            result, steps, exec_time = capture_algorithm_steps(
                fpgrowth,
                transactions_list,
                support_threshold,
                confidence_threshold
            )

            if result is None:
                return jsonify({'error': 'No frequent itemsets found with given thresholds'}), 400

            freqItems, rules = result

            # Calculate support for FP-Growth itemsets
            def calculate_support_for_itemset(itemset, transactions):
                count = 0
                for transaction in transactions:
                    if set(itemset).issubset(set(transaction)):
                        count += 1
                return count / len(transactions)

            # Format results for JSON
            formatted_itemsets = []
            for itemset in freqItems:
                support = calculate_support_for_itemset(itemset, transactions_list)
                formatted_itemsets.append({
                    'itemset': list(itemset),
                    'support': round(support, 4)
                })

            # Sắp xếp itemsets theo support giảm dần
            formatted_itemsets.sort(key=lambda x: x['support'], reverse=True)

            # Thêm số thứ tự
            for i, itemset in enumerate(formatted_itemsets, 1):
                itemset['rank'] = i

            formatted_rules = []
            for rule in rules:
                antecedent, consequent, confidence = rule
                formatted_rules.append({
                    'antecedent': list(antecedent),
                    'consequent': list(consequent),
                    'confidence': round(confidence, 4),
                    'description': format_rule_description(list(antecedent), list(consequent), confidence)
                })

            # Sắp xếp theo confidence từ cao xuống thấp
            formatted_rules.sort(key=lambda x: x['confidence'], reverse=True)

        # Clean up temporary files
        os.remove(temp_file_path)
        os.rmdir(temp_dir)

        # Prepare response
        response_data = {
            'success': True,
            'algorithm': algorithm,
            'parameters': {
                'support_threshold': support_threshold,
                'confidence_threshold': confidence_threshold
            },
            'data_info': {
                'total_transactions': len(transactions_list),
                'cleaning_time': round(clean_time, 4)
            },
            'results': {
                'frequent_itemsets': formatted_itemsets,
                'association_rules': formatted_rules,
                'execution_time': round(exec_time, 4),
                'steps': steps
            }
        }

        return jsonify(response_data)

    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error occurred: {str(e)}")
        print(f"Full traceback: {error_details}")
        return jsonify({'error': f'Error processing file: {str(e)}', 'details': error_details}), 500

@app.route('/compare', methods=['GET'])
def compare_results():
    """Compare custom algorithm results with library results"""
    try:
        global LIBRARY_RESULTS

        if LIBRARY_RESULTS is None:
            return jsonify({'error': 'No library results available. Please run algorithm first.'}), 400

        # Add product descriptions to library results
        if 'association_rules' in LIBRARY_RESULTS:
            for rule in LIBRARY_RESULTS['association_rules']:
                rule['description'] = format_rule_description(
                    rule['antecedent'],
                    rule['consequent'],
                    rule['confidence']
                )

        return jsonify({
            'success': True,
            'library_results': LIBRARY_RESULTS
        })

    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error in compare: {str(e)}")
        print(f"Full traceback: {error_details}")
        return jsonify({'error': f'Error comparing results: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=9005)
