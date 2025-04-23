from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
import os
from dotenv import load_dotenv

load_dotenv()

class ChatService:
    def __init__(self):
        self.llm = ChatOpenAI(
            model_name="gpt-3.5-turbo",
            temperature=0.7,
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        
        self.prompt = ChatPromptTemplate.from_template(
            """You are a car maintenance and repair assistant. Your goal is to help users with their vehicle maintenance needs.
            Use the following context to provide accurate and helpful responses:
            
            Vehicle Information:
            {vehicle_info}
            
            Previous Conversation:
            {chat_history}
            
            User's Question: {user_input}
            
            Please provide a helpful response focusing on car maintenance and repair. If the user's question is not related to car maintenance,
            politely redirect them to ask about car-related topics. Always be professional and informative."""
        )
        
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            input_key="user_input"
        )
        
        self.chain = LLMChain(
            llm=self.llm,
            prompt=self.prompt,
            memory=self.memory,
            verbose=True
        )

    def get_response(self, user_input: str, vehicle_info: dict = None) -> dict:
        try:
            # Format vehicle info for the prompt
            formatted_vehicle_info = ""
            if vehicle_info:
                formatted_vehicle_info = f"""
                Make: {vehicle_info.get('make', 'Unknown')}
                Model: {vehicle_info.get('model', 'Unknown')}
                Year: {vehicle_info.get('year', 'Unknown')}
                VIN: {vehicle_info.get('vin', 'Unknown')}
                """
            
            # Get response from the chain
            response = self.chain.run(
                user_input=user_input,
                vehicle_info=formatted_vehicle_info
            )
            
            # Generate relevant suggestions based on the conversation
            suggestions = self._generate_suggestions(user_input, vehicle_info)
            
            return {
                "response": response,
                "suggested_actions": suggestions
            }
            
        except Exception as e:
            print(f"Error in chat service: {str(e)}")
            return {
                "response": "I apologize, but I encountered an error. Please try again.",
                "suggested_actions": ["Try again", "Ask a different question"]
            }

    def _generate_suggestions(self, user_input: str, vehicle_info: dict = None) -> list:
        # Basic suggestions that are always relevant
        suggestions = [
            "Schedule maintenance",
            "View maintenance history",
            "Get maintenance cost estimate"
        ]
        
        # Add vehicle-specific suggestions if vehicle info is available
        if vehicle_info:
            suggestions.extend([
                f"Check {vehicle_info.get('make', '')} {vehicle_info.get('model', '')} maintenance schedule",
                f"Find parts for {vehicle_info.get('make', '')} {vehicle_info.get('model', '')}",
                f"Get {vehicle_info.get('year', '')} {vehicle_info.get('make', '')} service manual"
            ])
        
        return suggestions

# Create a singleton instance
chat_service = ChatService() 