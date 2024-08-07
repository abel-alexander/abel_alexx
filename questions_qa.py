
def clean_text(text):
    """Remove unwanted characters like tabs and question numbers."""
    text = text.replace('\t', '').strip()
    text = re.sub(r'^\d+\.\s*', '', text)  # Remove question numbers
    text = text.strip()
    return text

def get_questions_and_answers_from_excel(section, excel_path):
    questions_df = pd.read_excel(excel_path)
    section_df = questions_df[['Q&A', section]].dropna()

    extracted_data = []

    for _, row in section_df.iterrows():
        company = row['Q&A']
        questions_answers = row[section].split('\n') if pd.notna(row[section]) else []

        i = 0
        while i < len(questions_answers):
            question = clean_text(questions_answers[i])
            if question and not question.startswith('a.'):
                reference_answer = ""
                if (i + 1) < len(questions_answers):
                    answer_candidate = questions_answers[i + 1].strip()
                    if answer_candidate.startswith('a.'):
                        reference_answer = answer_candidate[2:].strip()  # Remove 'a.' prefix
                        i += 1  # Skip the answer line
                extracted_data.append({
                    'Company': company,
                    'Section': section,
                    'Question': question,
                    'Reference Answer': reference_answer
                })
            i += 1
    
    return pd.DataFrame(extracted_data)

def perform_qa_for_section(section, base_path, excel_path):
    section_path = os.path.join(base_path, 'extracted_data', section)
    output_folder = os.path.join(section_path, "QA_results")
    
    # Create the output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # Initialize LLM and embeddings
    llm = HuggingFaceLLM(
        context_window=4096,
        max_new_tokens=512,
        generate_kwargs={"temperature": 0.2, "do_sample": False},
        system_prompt="system-prompt",
        query_wrapper_prompt="query_wrapper_prompt",
        template_name="meta-llama/Llama-2-7b-chat-hf",
        model_name="meta-llama/Llama-2-7b-chat-hf",
        device_map="auto",
        model_kwargs={"torch_dtype": "torch.float16", "load_in_8bit": True}
    )
    
    embed_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
    service_context = ServiceContext.from_defaults(chunk_size=1024, llm=llm, embed_model=embed_model)

    # Load questions and answers from Excel
    qa_df = get_questions_and_answers_from_excel(section, excel_path)

    # Iterate over each file in the section folder
    for file_name in os.listdir(section_path):
        if file_name.endswith(".txt"):  # Assuming the documents are text files
            file_path = os.path.join(section_path, file_name)
            
            # Debugging print statements
            print(f"Processing file: {file_path}")
            print(f"File exists: {os.path.exists(file_path)}")
            
            company_name = os.path.splitext(file_name)[0]  # Extract company name from file name
            
            # Read the document
            with open(file_path, 'r', encoding='utf-8') as file:
                document_text = file.read()
            
            # Create a list of documents for the index
            documents = [{"text": document_text, "metadata": {"source": file_path}}]
            
            # Create index from document
            index = VectorStoreIndex.from_documents(documents, service_context=service_context)
            query_engine = index.as_query_engine()
            
            # Get questions and reference answers for the current company
            company_data = qa_df[qa_df['Company'] == company_name]
            
            # Open a file to write the QA results for this document
            result_file_name = f"{company_name}_qa_results.txt"
            result_file_path = os.path.join(output_folder, result_file_name)
            
            with open(result_file_path, 'w') as result_file:
                # Perform the queries for each document
                for _, row in company_data.iterrows():
                    question = row['Question']
                    reference_answer = row['Reference Answer']
                    response = query_engine.query(question)
                    result_file.write(f"Question: {question}\n")
                    result_file.write(f"Reference Answer: {reference_answer}\n")
                    result_file.write(f"Response: {response}\n\n")
            
            print(f"QA results saved to {result_file_path}")

# Example usage
perform_qa_for_section('10K', '/phoenix/workspaces/zk9zkma/Image_text_extraction/output_sections', '/path/to/your/questions.xlsx')
