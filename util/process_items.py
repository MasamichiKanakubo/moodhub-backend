from concurrent.futures import ThreadPoolExecutor

def process_item(item):
    # 単純な処理の例（実際にはより複雑な処理が含まれるかもしれません）
    return item * item

def process_items(items):
    with ThreadPoolExecutor() as executor:
        results = executor.map(process_item, items)
    return list(results)