import faiss, csv
from sentence_transformers import SentenceTransformer






# Read history with just required data (Might be deprecated due to langchain native InMemorySaver())
def history_reader(user_inp):
    model = SentenceTransformer('all-MiniLM-L6-v2')

    try:
        with open("history.csv", "r", encoding="utf-8") as f:
            data = f.read().splitlines()    # CHANGE SPLITLINES 
    except FileNotFoundError:
        data = []

    if not data:
        return 

    vectors = model.encode(data, convert_to_numpy=True)

    if vectors.ndim == 1:
        vectors = vectors.reshape(1, -1)

    vec_dimension = vectors.shape[1]

    index = faiss.IndexFlatL2(vec_dimension)
    index.add(vectors.astype('float32'))

    prompt_vector = model.encode([user_inp]).astype('float32')
    D, I = index.search(prompt_vector, k=15)

    return [data[idx] for idx in I[0]]






# Embedded transactions
def embedded_transact(user_inp, iter=10):
    """The embedding function that reads the transactions list and 'chooses' the relevant ones."""
    
    model = SentenceTransformer('all-MiniLM-L6-v2')

    rows = []
    with open("trans.csv", "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)    

    data=[f"{x['Date']} {x['Name']} {x['Amount']}" for x in rows]
    vectors = model.encode(data, convert_to_numpy=True)

    vec_dimension = vectors.shape[1]
    index = faiss.IndexFlatL2(vec_dimension)
    index.add(vectors)

    faiss.write_index(index, "trans.index") 
    index_read = faiss.read_index("trans.index")
    
    prompt_vector = model.encode([str(user_inp)])

    D, I = index_read.search(prompt_vector, k=iter)

    return [data[idx] for idx in I[0]]