from itertools import chain, combinations
from collections import defaultdict

def generate_all_subsets(element_list):
    """Generate all non-empty subsets from input element list"""
    return chain.from_iterable(combinations(element_list, length) for length in range(1, len(element_list)+1))


def filter_frequent_itemsets(candidates, transaction_list, min_support_threshold, global_counter, step_name=""):
    """Filter candidate itemsets based on minimum support threshold with detailed print"""
    qualifying_itemsets = set()
    temporary_counter = defaultdict(int)

    print(f"\n{'='*60}")
    print(f"STEP: {step_name}")
    print(f"{'='*60}")
    print(f"Checking {len(candidates)} candidate itemsets with min support = {min_support_threshold}")
    print(f"Total transactions: {len(transaction_list)}")
    print(f"-" * 60)

    # Count occurrences of each candidate in transactions
    candidates_with_support = []
    for candidate in candidates:
        count = 0
        for transaction in transaction_list:
            if candidate.issubset(transaction):
                count += 1

        support_ratio = count / len(transaction_list)
        candidates_with_support.append((candidate, count, support_ratio))

        # SỬA: Chỉ update global_counter một lần với count chính xác
        global_counter[candidate] = count

    # Sort by support descending for better readability
    candidates_with_support.sort(key=lambda x: x[2], reverse=True)

    print("Candidate itemsets and their support:")
    for candidate, count, support_ratio in candidates_with_support:
        candidate_str = str(tuple(sorted(candidate)))
        status = "✓ FREQUENT" if support_ratio >= min_support_threshold else "✗ Not frequent"
        print(f"  {candidate_str:<25} | Count: {count:2d} | Support: {support_ratio:.3f} | {status}")

        if support_ratio >= min_support_threshold:
            qualifying_itemsets.add(candidate)

    print(f"\nRESULT: {len(qualifying_itemsets)} frequent itemsets found")
    if qualifying_itemsets:
        frequent_list = [tuple(sorted(itemset)) for itemset in qualifying_itemsets]
        frequent_list.sort()
        print(f"Frequent itemsets: {frequent_list}")
    else:
        print("No frequent itemsets found - algorithm will terminate")

    return qualifying_itemsets


def combine_itemsets(current_itemsets, target_size):
    """Combine current itemsets to create itemsets of target size"""
    new_itemsets = []
    itemset_list = list(current_itemsets)

    print(f"\n{'='*60}")
    print(f"GENERATING {target_size}-ITEMSET CANDIDATES")
    print(f"{'='*60}")
    print(f"Combining {len(itemset_list)} frequent {target_size-1}-itemsets:")

    # Show current frequent itemsets
    current_list = [tuple(sorted(itemset)) for itemset in itemset_list]
    current_list.sort()
    for itemset in current_list:
        print(f"  {itemset}")

    for i in range(len(itemset_list)):
        for j in range(i+1, len(itemset_list)):
            union_set = itemset_list[i].union(itemset_list[j])
            if len(union_set) == target_size:
                new_itemsets.append(union_set)

    # SỬA: Remove duplicates properly
    unique_itemsets = set()
    for itemset in new_itemsets:
        unique_itemsets.add(itemset)
    new_itemsets = list(unique_itemsets)

    print(f"\nGenerated {len(new_itemsets)} candidates:")
    candidates_list = [tuple(sorted(itemset)) for itemset in new_itemsets]
    candidates_list.sort()
    for candidate in candidates_list:
        print(f"  {candidate}")

    return set(new_itemsets)


def generate_association_rules(frequent_itemsets_result, frequency_counter, transactions, confidence_threshold):
    """Generate association rules with detailed print"""
    association_rules_list = []
    # SỬA: Sử dụng set để tránh duplicate rules
    unique_rules = set()

    print(f"\n{'='*60}")
    print(f"GENERATING ASSOCIATION RULES")
    print(f"{'='*60}")
    print(f"Minimum confidence threshold: {confidence_threshold}")
    print(f"Only considering itemsets with 2+ elements")

    # Only consider itemsets with at least 2 elements
    for size, itemsets in list(frequent_itemsets_result.items())[1:]:
        print(f"\n{'-'*60}")
        print(f"Processing frequent {size}-itemsets:")
        print(f"{'-'*60}")

        for original_itemset in itemsets:
            itemset_tuple = tuple(sorted(original_itemset))
            itemset_support = frequency_counter[original_itemset] / len(transactions)
            print(f"\nItemset: {itemset_tuple} (support = {itemset_support:.3f})")
            print(f"Generating all possible rules:")

            # Generate all non-empty subsets
            all_subsets = map(frozenset, [x for x in generate_all_subsets(original_itemset)])

            rules_from_this_itemset = []
            for subset in all_subsets:
                remaining_set = original_itemset.difference(subset)

                if len(remaining_set) > 0:
                    subset_support = frequency_counter[subset] / len(transactions)
                    confidence = frequency_counter[original_itemset] / frequency_counter[subset]

                    antecedent = tuple(sorted(subset))
                    consequent = tuple(sorted(remaining_set))

                    status = "✓ ACCEPTED" if confidence >= confidence_threshold else "✗ REJECTED"

                    print(f"  {antecedent} => {consequent}")
                    print(f"    Confidence = support({itemset_tuple}) / support({antecedent})")
                    print(f"    Confidence = {itemset_support:.3f} / {subset_support:.3f} = {confidence:.3f}")
                    print(f"    {status} (threshold = {confidence_threshold})")

                    if confidence >= confidence_threshold:
                        # SỬA: Tạo unique key cho rule để tránh duplicate
                        rule_key = (antecedent, consequent)
                        if rule_key not in unique_rules:
                            unique_rules.add(rule_key)
                            new_rule = ((antecedent, consequent), confidence)
                            association_rules_list.append(new_rule)
                            rules_from_this_itemset.append(new_rule)
                    print()

            if rules_from_this_itemset:
                print(f"  Accepted rules from {itemset_tuple}: {len(rules_from_this_itemset)}")
            else:
                print(f"  No rules accepted from {itemset_tuple}")

    print(f"\n{'='*60}")
    print(f"ASSOCIATION RULES SUMMARY")
    print(f"{'='*60}")
    print(f"Total rules generated: {len(association_rules_list)}")

    return association_rules_list


def process_raw_data(raw_data):
    """Convert raw data into transaction list and single items"""
    transactions = []
    single_items = set()

    print(f"{'='*60}")
    print(f"DATA PREPROCESSING")
    print(f"{'='*60}")
    print(f"📊 Total transactions: {len(raw_data)}")

    # Show first 5 transactions as examples
    print("📋 Sample transactions:")
    for i, record in enumerate(raw_data[:5], 1):
        current_transaction = frozenset(record)
        transactions.append(current_transaction)

        items_display = ', '.join(sorted(record)[:5])  # Show first 5 items
        if len(record) > 5:
            items_display += f" ... (+{len(record)-5} more items)"
        print(f"  • Transaction {i}: [{items_display}]")

        # Create single items (1-itemsets)
        for item in current_transaction:
            single_items.add(frozenset([item]))

    # Process remaining transactions
    for i, record in enumerate(raw_data[5:], 6):
        current_transaction = frozenset(record)
        transactions.append(current_transaction)

        # Create single items (1-itemsets)
        for item in current_transaction:
            single_items.add(frozenset([item]))

    if len(raw_data) > 5:
        print(f"  ... and {len(raw_data)-5} more transactions")

    unique_items = sorted([list(item)[0] for item in single_items])
    print(f"\n📈 Analysis summary:")
    print(f"  • Total transactions: {len(transactions)}")
    print(f"  • Unique items found: {len(single_items)}")
    print(f"  • Items: {', '.join(unique_items[:10])}{'...' if len(unique_items) > 10 else ''}")

    return single_items, transactions


def main_apriori_algorithm(data, support_threshold, confidence_threshold):
    """Main function to run Apriori algorithm with detailed output"""

    print(f"{'#'*60}")
    print(f"APRIORI ALGORITHM - DETAILED EXECUTION")
    print(f"{'#'*60}")
    print(f"Support threshold: {support_threshold}")
    print(f"Confidence threshold: {confidence_threshold}")

    # Step 1: Prepare data
    single_items, transactions = process_raw_data(data)

    # Initialize storage variables
    frequency_counter = defaultdict(int)
    frequent_itemsets_result = {}

    # Step 2: Find frequent 1-itemsets
    current_frequent_itemsets = filter_frequent_itemsets(
        single_items, transactions, support_threshold, frequency_counter,
        "Finding Frequent 1-itemsets"
    )

    # Step 3: Iterate to find frequent k-itemsets
    size_index = 2
    while len(current_frequent_itemsets) > 0:
        # Store results of (k-1)-itemsets
        frequent_itemsets_result[size_index - 1] = current_frequent_itemsets

        # Generate new k-itemset candidates
        new_candidates = combine_itemsets(current_frequent_itemsets, size_index)

        if new_candidates:
            # Filter candidates that meet support threshold
            current_frequent_itemsets = filter_frequent_itemsets(
                new_candidates, transactions, support_threshold, frequency_counter,
                f"Finding Frequent {size_index}-itemsets"
            )
        else:
            current_frequent_itemsets = set()

        size_index += 1

    # Helper function to calculate support
    def calculate_support(itemset):
        return frequency_counter[itemset] / len(transactions)

    # SỬA: Step 4: Prepare final itemset results - tránh duplicate
    final_itemset_list = []
    seen_itemsets = set()

    for size, itemsets in frequent_itemsets_result.items():
        for itemset in itemsets:
            itemset_tuple = tuple(sorted(itemset))
            if itemset_tuple not in seen_itemsets:
                seen_itemsets.add(itemset_tuple)
                itemset_support = calculate_support(itemset)
                final_itemset_list.append((itemset_tuple, itemset_support))

    # Step 5: Generate association rules
    association_rules_list = generate_association_rules(
        frequent_itemsets_result, frequency_counter, transactions, confidence_threshold
    )

    return final_itemset_list, association_rules_list


def print_final_results(itemsets, rules, support_threshold, confidence_threshold):
    """Print final summary results"""
    print(f"\n{'#'*60}")
    print(f"FINAL RESULTS SUMMARY")
    print(f"{'#'*60}")

    print(f"\nFREQUENT ITEMSETS (support >= {support_threshold}):")
    print(f"{'-'*40}")

    # SỬA: Group by size properly
    itemsets_by_size = {}
    for itemset, support in itemsets:
        size = len(itemset)
        if size not in itemsets_by_size:
            itemsets_by_size[size] = []
        itemsets_by_size[size].append((itemset, support))

    # Print by size
    for size in sorted(itemsets_by_size.keys()):
        print(f"\n{size}-itemsets:")
        # Sort by itemset name for consistent output
        sorted_itemsets = sorted(itemsets_by_size[size], key=lambda x: x[0])
        for itemset, support in sorted_itemsets:
            print(f"  {itemset}: support = {support:.3f}")

    print(f"\nASSOCIATION RULES (confidence >= {confidence_threshold}):")
    print(f"{'-'*40}")
    if rules:
        # SỬA: Sort theo confidence descending, không duplicate
        for (antecedent, consequent), confidence in sorted(rules, key=lambda x: -x[1]):
            print(f"  {antecedent} => {consequent}: confidence = {confidence:.3f}")
    else:
        print("  No association rules found with the given thresholds.")

    print(f"\nSTATISTICS:")
    print(f"  Total frequent itemsets: {len(itemsets)}")
    print(f"  Total association rules: {len(rules)}")


# Usage example
if __name__ == "__main__":
    # Sample data
    sample_data = [
        ['B', 'C'],
        ['A', 'B'],
        ['A', 'C'],
        ['B', 'C'],
        ['A', 'B', 'C']
    ]

    # Run algorithm
    itemsets, rules = main_apriori_algorithm(sample_data, 0.4, 0.6)

    # Print final results
    print_final_results(itemsets, rules, 0.4, 0.6)
