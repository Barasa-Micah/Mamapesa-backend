def  get_all_transactions(all_savings_items):
    all_transactions=list()
    # loop through all saving items
    for each_saving_item in all_savings_items:
        # loop through each transaction while adding it to the transactions list
        for each_transaction in each_saving_item.transactions.all():
            all_transactions.append(each_transaction)
    return all_transactions 