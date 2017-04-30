from pymongo import MongoClient


def remove_duplicates_in_mongodb_collection(db_name, collection_name, unique_keys):
    """
    :param db_name: str
        Name of database to scan for duplicates
    :param collection_name: str
        Name of collection  of database to scan for duplicates
    :param unique_keys: [] of str
        List of keys that must be unique
    :return: void
        Removes all items (but one) with 2 equal unique_keys
    """

    mongodb_client = MongoClient()  # mongodb client
    db = mongodb_client[db_name]  # database to use
    coll = db[collection_name]
    if coll.count() > 1:  # scan for duplicates if there are at least 2 items in collection
        print("Before scanning for duplicates collection \"" + str(collection_name) + "\" has", coll.count(),
              "elements.")

        for mongodb_obj in coll.find():  # iterate through items in collection
            d = {}  # dictionary to find duplicates (based on unique keys of object)
            for k in unique_keys:
                d[k] = mongodb_obj[k]
            mongodb_obj_duplicates = coll.find(d)  # find objects ==
            if mongodb_obj_duplicates.count() > 1:  # if there is more than one duplicate (one is the obj itself)
                print("\tFound", mongodb_obj_duplicates.count(), "duplicates of", mongodb_obj["_id"])

                # TODO: WTF coll.delete_many(list(mongodb_obj_duplicates)[1:])  # remove all but one

        print("After scanning for duplicates collection \"" + str(collection_name) + "\" has",
              coll.count(), "elements.")
    else:
        print("No duplicates in collection \"" + str(collection_name) + "\"!")


def remove_duplicates_in_mongodb(db_name, unique_keys):
    """
    :param db_name: str
        Name of database to scan for duplicates
    :param unique_keys: [] of str
        List of keys that must be unique
    :return: void
        Removes all items (but one) with 2 equal unique_keys
    """

    mongodb_client = MongoClient()  # mongodb client
    db = mongodb_client[db_name]  # database to use
    for c in db.collection_names():
        remove_duplicates_in_mongodb_collection(db_name, c, unique_keys)
