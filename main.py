import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import pydeck as pdk
from langchain.prompts import PromptTemplate
from langchain.vectorstores import Chroma
from langchain.llms import Ollama
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.chains import RetrievalQA
from langchain.embeddings import GPT4AllEmbeddings
from collections import Counter

# ia m using chroma as a vectordb for storing my embed data
chroma_storage_dir = "chroma_storage" 
embedding_function = GPT4AllEmbeddings()
vectorstore = Chroma(persist_directory=chroma_storage_dir, embedding_function=embedding_function)
#  You can use any model you like for text-generation
# i have used llama2 for text-generation
llm = Ollama(model="llama2", verbose=False, callback_manager=CallbackManager([StreamingStdOutCallbackHandler()]))

QA_CHAIN_PROMPT = PromptTemplate(
    input_variables=["question", "context"],
    template="""Use the following pieces of retrieved context to answer the question concisely.

    Question: {question}

    Context: {context}

    Answer:"""
)
# this is the chain for specific document retrivation
qa_chain = RetrievalQA.from_chain_type(
    llm,
    retriever=vectorstore.as_retriever(),
    chain_type_kwargs={"prompt": QA_CHAIN_PROMPT},
)

st.title("EV Data Search and Analysis Web Application")
#  this will get the context of question ans use it as session
if 'questions' not in st.session_state:
    st.session_state.questions = []
if 'answers' not in st.session_state:
    st.session_state.answers = []

locations = pd.DataFrame({
    'latitude': [37.7749, 34.0522, 40.7128],
    'longitude': [-122.4194, -118.2437, -74.0060],
    'location': ['San Francisco', 'Los Angeles', 'New York']
})

st.subheader("Map of Locations")
map_layer = pdk.Layer(
    "ScatterplotLayer",
    data=locations,
    get_position=["longitude", "latitude"],
    get_color=[255, 0, 0, 160],
    get_radius=50000,
    pickable=True,
    auto_highlight=True
)

view_state = pdk.ViewState(
    latitude=locations['latitude'].mean(),
    longitude=locations['longitude'].mean(),
    zoom=4,
    pitch=0
)

deck = pdk.Deck(
    layers=[map_layer],
    initial_view_state=view_state,
    tooltip={"text": "{location}"}
)

st.pydeck_chart(deck)
# thi will ask for query from the user as question
question = st.text_input("Enter your question:")

if st.button("Ask"):
    if question:
        try:
            result = qa_chain({"query": question})
            answer = result['result']
            st.session_state.questions.append(question)
            st.session_state.answers.append(answer)
            
            st.write("**Answer:**", answer)
            
            keywords = [word.lower() for word in answer.split()]
            keyword_freq = Counter(keywords)
            
            df = pd.DataFrame(keyword_freq.items(), columns=['Keyword', 'Frequency'])
            df = df.sort_values(by='Frequency', ascending=False)

            fig, ax = plt.subplots()
            ax.bar(df['Keyword'], df['Frequency'], color='skyblue')
            ax.set_xlabel('Keywords')
            ax.set_ylabel('Frequency')
            ax.set_title('Keyword Frequency in Answers')
            plt.xticks(rotation=45)
            st.pyplot(fig)
            
        except Exception as e:
            st.error(f"Error: {str(e)}")
    else:
        st.error("Please provide a question.")

# this is streamlit session handler 
if st.session_state.questions:
    st.subheader("Previous Questions and Answers")
    for q, a in zip(st.session_state.questions, st.session_state.answers):
        st.write(f"**Q:** {q}")
        st.write(f"**A:** {a}")
