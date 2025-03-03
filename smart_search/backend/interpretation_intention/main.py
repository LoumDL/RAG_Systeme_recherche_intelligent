
from model.llm import llm



def chatbox(question: str):
   
    
    resultats = llm(question)
    #print(resultats)
    return resultats




if __name__ == "__main__":
    question = input("Posez votre question :  ")
    resl = chatbox(question)
    print(resl)
