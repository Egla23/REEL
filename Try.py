from utils import get_chroma_client, get_or_create_collection,query_collection,format_results_as_context

def main():
    print("hello")
    # call functions here
    client = get_chroma_client("./chroma_db")
    collection = get_or_create_collection(client, "docs")

    i = input()
    while i != 'q': # loops indefinatley until input is 'q'
        results = query_collection(collection, i, n_results=3)
        contexts= format_results_as_context(results) 
        print(contexts)
        i = input()
    
    print('ended')
if __name__ == "__main__":
    main() # will run main when you click run


