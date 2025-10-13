from datasets import load_dataset

# 1. SQuAD (Question Answering)
squad = load_dataset("squad_v2")

# 2. Natural Questions
#nq = load_dataset("natural_questions")

# 3. HotpotQA (Multi-hop reasoning)
#hotpot = load_dataset("hotpot_qa")

# 4. MS MARCO (Document ranking)
#marco = load_dataset("ms_marco", "v2.1")
print(squad['train'][0])