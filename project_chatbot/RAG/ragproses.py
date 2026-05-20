from sentence_transformers import SentenceTransformer
import psycopg2
import cohere


from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import ast


# =========================
# COHERE CLIENT
# =========================
co = cohere.ClientV2("jvvF0hEiBCsJENHbklV7aMPWXF6gxGvt03ifPYYI")


# =========================
# EMBEDDING
# =========================
def embeeding_knowledge(input):
    model = SentenceTransformer('firqaaa/indo-sentence-bert-base')
    embeddings = model.encode(input,normalize_embeddings=True)
    return embeddings


# =========================
# DATABASE CONNECTION
# =========================
def get_connection():

    conn = psycopg2.connect(
        dbname="postgres",
        user="postgres",
        password="root",
        host="localhost"
    )

    return conn


# =========================
# INSERT KNOWLEDGE
# =========================
def input_knowledge(id, question, answer):

    try:
        conn = get_connection()
        curr = conn.cursor()

        embeeding_question = embeeding_knowledge(question)
        embedding_str = str(embeeding_question.tolist())

        querry = """
        INSERT INTO questiondb
        (id, pertanyaan, jawaban, embedding)
        VALUES (%s, %s, %s, %s)
        """

        curr.execute(
            querry,
            (id, question, answer, embedding_str)
        )

        conn.commit()
        conn.close()

        print("Sukses insert ke database")

    except Exception as e:
        print("Error saat insert ke database", e)


# =========================
# VECTOR SEARCH
# =========================
def get_similarity_search(question_user):

    embeed_question = embeeding_knowledge(question_user)
    embeedstring = str(embeed_question.tolist())

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    SELECT
        id,
        pertanyaan,
        jawaban,
        1 - (embedding <=> %s::vector) AS cosine_similarity

    FROM questiondb

    ORDER BY cosine_similarity DESC
    LIMIT 5;
    """, (embeedstring,))

    rows = cur.fetchall()

    print("Hasil similarity search",rows)

    conn.close()

    return rows


# def similarity_search(question_user):

#     query_embedding = embeeding_knowledge(question_user)

#     conn = get_connection()

#     cur = conn.cursor()

#     cur.execute("""
#         SELECT
#             id,
#             pertanyaan,
#             jawaban,
#             embedding
#         FROM questiondb
#     """)

#     rows = cur.fetchall()

#     results = []

#     for row in rows:

#         id_data = row[0]
#         pertanyaan = row[1]
#         jawaban = row[2]

#         # convert string -> list
#         embedding_db = ast.literal_eval(row[3])

#         embedding_db = np.array(
#             embedding_db
#         ).reshape(1, -1)

#         query_embedding_2d = np.array(
#             query_embedding
#         ).reshape(1, -1)

#         score = cosine_similarity(
#             query_embedding_2d,
#             embedding_db
#         )[0][0]

#         results.append({
#             "id": id_data,
#             "pertanyaan": pertanyaan,
#             "jawaban": jawaban,
#             "score": float(score)
#         })

#     # sort descending
#     results = sorted(
#         results,
#         key=lambda x: x["score"],
#         reverse=True
#     )

#     conn.close()

#     print("Hasil similarity search",results)

#     return results[:5]


# =========================
# KEYWORD SEARCH
# =========================
def get_keyword_search(question_user):

    conn = get_connection()
    cur = conn.cursor()

    query = """
    SELECT
        id,
        pertanyaan,
        jawaban,

        ts_rank(
            search_vector,
            plainto_tsquery(
                'indonesian',
                %s
            )
        ) AS score

    FROM questiondb

    WHERE search_vector @@ plainto_tsquery(
        'indonesian',
        %s
    )

    ORDER BY score DESC
    LIMIT 5;
    """

    cur.execute(query, (question_user, question_user))

    results = cur.fetchall()

    cur.close()
    conn.close()

    return results


# =========================
# COHERE RERANK
# =========================
def rerank_results(question_user, documents):

    docs = []

    for doc in documents:

        docs.append(
            f"""
            Pertanyaan: {doc[1]}

            Jawaban:
            {doc[2]}
            """
        )

    response = co.rerank(
        model="rerank-v3.5",
        query=question_user,
        documents=docs,
        top_n=5
    )

    reranked_results = []

    for result in response.results:

        original_doc = documents[result.index]

        reranked_results.append({
            "id": original_doc[0],
            "pertanyaan": original_doc[1],
            "jawaban": original_doc[2],
            "relevance_score": result.relevance_score
        })

    return reranked_results


# =========================
# HYBRID SEARCH
# =========================
def hybrid_search(question_user):

    vector_results = get_similarity_search(question_user)

    keyword_results = get_keyword_search(question_user)

    # combine results
    combined = vector_results + keyword_results

    # remove duplicate id
    unique_results = {}

    for row in combined:
        unique_results[row[0]] = row

    final_results = list(unique_results.values())

    # rerank
    reranked = rerank_results(
        question_user,
        final_results
    )


    return reranked


# =========================
# TEST
# =========================
results = hybrid_search(
    "Produk apa saja yang cocok kulit berjerawat"
)

for r in results:
    print("=" * 50)
    print("ID:", r["id"])
    print("Pertanyaan:", r["pertanyaan"])
    print("Jawaban:", r["jawaban"])
    print("Score:", r["relevance_score"])










