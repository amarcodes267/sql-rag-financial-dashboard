import streamlit as st
import pandas as pd

from database.database import (
    initialize_database,
    insert_company,
    insert_financial_data,
    get_financial_data
)

from extraction.pdf_extractor import (
    extract_text_from_pdf
)

from extraction.financial_extractor import (
    extract_financial_data
)

from rag.vector_store import (
    clear_collection,
    add_documents
)

from hybrid.query_router import (
    process_question
)

from dashboard.metrics import (
    calculate_metrics
)

from dashboard.charts import (
    revenue_chart,
    profit_chart,
    assets_liabilities_chart
)

from utils.helpers import (
    save_uploaded_file
)


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Financial Intelligence Dashboard",
    page_icon="📊",
    layout="wide"
)


# ============================================================
# DATABASE
# ============================================================

initialize_database()


# ============================================================
# HEADER
# ============================================================

st.title("📊 Financial Intelligence Dashboard")

st.caption(
    "SQL + RAG powered financial analysis"
)


# ============================================================
# SIDEBAR - PDF UPLOAD
# ============================================================

with st.sidebar:

    st.header("📄 Financial Report")

    uploaded_file = st.file_uploader(
        "Upload Financial PDF",
        type=["pdf"]
    )

    process_button = st.button(
        "Process Financial Report",
        use_container_width=True
    )


# ============================================================
# PROCESS PDF
# ============================================================

if process_button:

    if uploaded_file is None:

        st.error(
            "Please upload a financial PDF first."
        )

    else:

        with st.spinner(
            "Processing financial report..."
        ):

            try:

                # Save PDF
                file_path = save_uploaded_file(
                    uploaded_file
                )

                # Extract PDF text
                pages = extract_text_from_pdf(
                    file_path
                )

                if not pages:

                    st.error(
                        "No readable text found in the PDF."
                    )

                    st.stop()

                # Combine PDF text
                full_text = "\n\n".join(
                    page["text"]
                    for page in pages
                )

                # Extract structured financial data
                financial_data = (
                    extract_financial_data(
                        full_text
                    )
                )

                company_name = (
                    financial_data.get(
                        "company",
                        "Unknown Company"
                    )
                )

                # Store company
                company_id = insert_company(
                    company_name
                )

                # Clear previous RAG data
                clear_collection()

                # Store PDF pages in vector database
                add_documents(
                    pages
                )

                # Store financial data in SQL
                for item in financial_data.get(
                    "financial_data",
                    []
                ):

                    if item.get("year") is not None:

                        insert_financial_data(
                            company_id,
                            item
                        )

                st.session_state[
                    "processed"
                ] = True

                st.session_state[
                    "company"
                ] = company_name

                st.success(
                    "Financial report processed successfully!"
                )

                st.rerun()

            except Exception as error:

                st.error(
                    f"Processing failed: {error}"
                )


# ============================================================
# LOAD FINANCIAL DATA
# ============================================================

data = get_financial_data()


if not data:

    st.info(
        "👈 Upload a financial PDF from the sidebar to begin."
    )

    st.stop()


df = pd.DataFrame(data)


# ============================================================
# COMPANY NAME
# ============================================================

company_name = df["company"].iloc[0]

st.header(
    f"Financial Overview — {company_name}"
)


# ============================================================
# METRICS
# ============================================================

metrics = calculate_metrics(
    data
)

col1, col2, col3, col4 = st.columns(4)


with col1:

    st.metric(
        "Revenue",
        f"{metrics['revenue']:,.2f}"
    )


with col2:

    st.metric(
        "Net Profit",
        f"{metrics['profit']:,.2f}"
    )


with col3:

    st.metric(
        "Total Assets",
        f"{metrics['assets']:,.2f}"
    )


with col4:

    st.metric(
        "Revenue Growth",
        f"{metrics['growth']:.2f}%"
    )


# ============================================================
# CHARTS
# ============================================================

st.subheader(
    "📈 Financial Performance"
)

chart_col1, chart_col2 = st.columns(2)


with chart_col1:

    chart = revenue_chart(
        data
    )

    if chart:

        st.plotly_chart(
            chart,
            use_container_width=True
        )


with chart_col2:

    chart = profit_chart(
        data
    )

    if chart:

        st.plotly_chart(
            chart,
            use_container_width=True
        )


chart = assets_liabilities_chart(
    data
)

if chart:

    st.plotly_chart(
        chart,
        use_container_width=True
    )


# ============================================================
# STRUCTURED FINANCIAL DATA
# ============================================================

st.subheader(
    "📋 Structured Financial Data"
)

st.dataframe(
    df,
    use_container_width=True,
    hide_index=True
)


# ============================================================
# AI FINANCIAL ASSISTANT
# ============================================================

st.divider()

st.header(
    "🤖 Ask the Financial AI"
)

st.write(
    "Ask questions about the uploaded financial report. "
    "The system automatically uses SQL, RAG, or SQL + RAG."
)


# ============================================================
# EXAMPLE QUESTIONS
# ============================================================

st.markdown(
    "**Example questions:**"
)

example_col1, example_col2, example_col3 = st.columns(3)


with example_col1:

    st.info(
        "💰 What was Apple's revenue in 2025?"
    )


with example_col2:

    st.info(
        "📄 What are the major risks mentioned?"
    )


with example_col3:

    st.info(
        "📊 Why did Apple's revenue change?"
    )


# ============================================================
# QUESTION INPUT
# ============================================================

question = st.chat_input(
    "Ask a question about the financial report..."
)


# ============================================================
# QUESTION PROCESSING
# ============================================================

if question:

    # User question
    with st.chat_message("user"):

        st.write(
            question
        )


    # AI response
    with st.chat_message("assistant"):

        with st.spinner(
            "Analyzing the financial report..."
        ):

            try:

                result = process_question(
                    question
                )


                # ====================================================
                # FINAL ANSWER
                # ====================================================

                st.markdown(
                    result["answer"]
                )


                # ====================================================
                # ENGINE USED
                # ====================================================

                engine = result.get(
                    "type",
                    "RAG"
                )

                if engine == "SQL":

                    st.success(
                        "🔢 Answered using SQL"
                    )

                elif engine == "RAG":

                    st.success(
                        "📄 Answered using RAG"
                    )

                else:

                    st.success(
                        "🔀 Answered using SQL + RAG"
                    )


                # ====================================================
                # SQL RESULT ONLY
                # ====================================================

                if "data" in result:

                    if result["data"]:

                        with st.expander(
                            "📊 View SQL Result"
                        ):

                            st.dataframe(
                                pd.DataFrame(
                                    result["data"]
                                ),
                                use_container_width=True,
                                hide_index=True
                            )


                # ====================================================
                # HYBRID SQL RESULT ONLY
                # ====================================================

                if "sql_data" in result:

                    if result["sql_data"]:

                        with st.expander(
                            "📊 View SQL Result"
                        ):

                            st.dataframe(
                                pd.DataFrame(
                                    result["sql_data"]
                                ),
                                use_container_width=True,
                                hide_index=True
                            )


                # ====================================================
                # RAG ANALYSIS
                # ====================================================

                if "rag_answer" in result:

                    with st.expander(
                        "📄 View RAG Analysis"
                    ):

                        st.write(
                            result["rag_answer"]
                        )


            except Exception as error:

                st.error(
                    f"Unable to answer question: {error}"
                )