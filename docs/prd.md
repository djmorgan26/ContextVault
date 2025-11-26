Context Vault


MVP
- User can store personal data in a secure manner
    - No one but user has access
    - Data must be encoded or inaccessible to 3rd parties 
- User can call LLM without personal data being touched by 3rd party
- LLM can access personal data
- User can interact with LLM
    - ChatGPT like experience/GUI
- Things user might want to store in context vault include medical records, body measurements, reusable bits of context they like to use when interacting with llms (llm knowledge/preferences)
- Use markdown indexing method to dynamically reference to llm where to go to gather correct context


Storing personal data and LLM on device solves:
- downloading open source LLM is free
- chats never leave device so data and prompts are not seen by 3rd party
- Data never leaves device and not see by 3rd party
- When LLM calls personal data all interaction never involes 3rd party
-  GUI can be created via browser or desktop app
- Maybe use ephemeral container or VM that pulls local llm that can access your personal data but it won’t store any info. Drawback is that this solution is not as quick but user prefers this solution to being quick and insecure


Desired functionality that is not MVP
- personal data passively accumulated 
    - Linked so new data is added overtime in automated fashion without user interaction
- All functionality on any device or anywhere
- Fast responses from LLM
- Solved problem of local llm taking up too much storage on phone 
- Establishment gateway or easy transfer of knowledge to use 3rd party apps

How do we make this proprietary so that someone else can’t copy/surpass us easily 
- 
