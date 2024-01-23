from flask import Flask,render_template, request, jsonify
from langchain.embeddings import VertexAIEmbeddings
from google.cloud import aiplatform
import os
from dotenv import load_dotenv
from pgvector.asyncpg import register_vector
import asyncio
import asyncpg
from google.cloud.sql.connector import Connector


from langchain.chains.summarize import load_summarize_chain
from langchain.docstore.document import Document
from langchain.llms import VertexAI
from langchain import PromptTemplate, LLMChain


# os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "random-developments-e04ef5e166a4.json"
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "random-developments-ccb662eb0a8f.json"

# Please fill in these values.
project_id = "YOUR-PROJECT-ID"
database_password = "YOUR-PASSWORD"
region = "us-central1" # This should be your chosen region
instance_name = "moses-first-mysql" # The name of your SQL instance
database_name = "postgres" # The name of your database
database_user = "moses" # The user that you created

aiplatform.init(project=f"{project_id}", location=f"{region}")
embeddings_service = VertexAIEmbeddings()
# load_dotenv()
# PROJECT_ID = os.getenv('PROJECT_ID')
# LOCATION = os.getenv('LOCATION')
# CODE_CHAT_MODEL = os.getenv('CODE_CHAT_MODEL')

app = Flask(__name__)

llm = VertexAI(model_name='text-bison')

map_prompt_template = """
              You will be given a bible verse and some text.
              The text is enclosed in triple backticks (```)
              ```{text}```
              SUMMARY:
              """
map_prompt = PromptTemplate(template=map_prompt_template, input_variables=["text"])

combine_prompt_template = """
                You will be given a bible verse, some text
                and a question enclosed in double backticks(``).
                Based on the given text, answer the following
                question in as much detail as possible.
                You may include the bible verse in your description, but it is not compulsory.
                Do not repeat the bible verse as the answer.
                Your description should be done in such a way that it answers the question.
                


                Description:
                ```{text}```


                Question:
                ``{user_query}``


                Answer:
                """
combine_prompt = PromptTemplate(
    template=combine_prompt_template, input_variables=["text", "user_query"]
)

async def main(qe, matches):
    loop = asyncio.get_running_loop()
    async with Connector(loop=loop) as connector:
        # Create connection to Cloud SQL database.
        conn: asyncpg.Connection = await connector.connect_async(
            f"{project_id}:{region}:{instance_name}",  # Cloud SQL instance connection name
            "asyncpg",
            user=f"{database_user}",
            password=f"{database_password}",
            db=f"{database_name}",
        )

        await register_vector(conn)
        similarity_threshold = 0.1
        num_matches = 10

        # Find similar products to the query using cosine similarity search
        # over all vector embeddings. This new feature is provided by `pgvector`.
        results = await conn.fetch(
            """
                            WITH vector_matches AS (
                                SELECT row_id, 1 - (embedding <=> $1) AS similarity
                                FROM bible_embeddings
                                WHERE 1 - (embedding <=> $1) > $2
                                ORDER BY similarity DESC
                                LIMIT $3
                            )
                            SELECT row_id, content FROM bible_embeddings
                            WHERE row_id IN (SELECT row_id FROM vector_matches)
                            """,
            qe,
            similarity_threshold,
            num_matches
            )

        if len(results) == 0:
            raise Exception("Did not find any results. Adjust the query parameters.")

        for r in results:
            # Collect the description for all the matched similar toy products.
            matches.append(
                f"""The scripture passage is taken from {r["row_id"]}. While the text itself says: {r["content"]}."""
            )

        await conn.close()


@app.route("/")
def home():
    return render_template("index2.html")

@app.route("/get")
def get_bot_response():    
    userText = request.args.get('msg')
    qe = embeddings_service.embed_query([userText])
    matches = []
    asyncio.run(main(qe, matches))

    docs = [Document(page_content=t) for t in matches]

    matches.clear()

    chain = load_summarize_chain(
        llm, chain_type="map_reduce", map_prompt=map_prompt, combine_prompt=combine_prompt
    )
    answer = chain.run(
        {
            "input_documents": docs,
            "user_query": userText,
        }
    )

    return str(answer)


if __name__ == "__main__":
    app.run(debug=False)
