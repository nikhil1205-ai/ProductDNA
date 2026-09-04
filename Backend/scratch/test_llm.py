import os
from dotenv import load_dotenv

load_dotenv()

# We'll use the exact same LangChain setup that Module 5 uses to verify it works
try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain_core.messages import HumanMessage
    
    api_key = os.getenv("GEMINI_API_KEY")
    print(f"API Key found: {'Yes (length: ' + str(len(api_key)) + ')' if api_key else 'No'}")
    
    if not api_key:
        print("Cannot test LLM: No API key found in .env")
        exit(1)
        
    print("\nInitializing LangChain Gemini model...")
    llm = ChatGoogleGenerativeAI(
        model=os.getenv("LLM_MODEL", "gemini-1.5-flash"),
        google_api_key=api_key,
        temperature=0.0
    )
    
    print("Sending test message...")
    response = llm.invoke([HumanMessage(content="Reply with exactly 'LLM is working!'")])
    
    print("\n--- Result ---")
    print(f"Status: SUCCESS")
    print(f"Response: {response.content}")
    
except ImportError as e:
    print(f"Missing dependency: {e}")
except Exception as e:
    print(f"\n--- Result ---")
    print(f"Status: FAILED")
    print(f"Error: {str(e)}")
