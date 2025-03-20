
from rejection_patterns import RejectionPattern

rejection_pattern = RejectionPattern()

r1 = rejection_pattern.detect(title='SQD (fka Subsquid) - Public data indexing Infrastructure for Polkadot and Kusama (Q2 2024)', content='UPD. Please reject this proposal; we will resubmit it in stablecoins.')
print(r1)  # {'is_nay_request': True, 'confidence': 0.95, 'explanation': "Strong indicator: 'reject this proposal'"}

r2 = rejection_pattern.detect(title='Small Tips retroactive for Content in Portuguese UPDATED (Vote Nay - if you set AYE Change your vote to NAY)', content='Updated Situation: Hello @Polkadot friends VOTE NAY to referendum 144, we are currently going to pau')
print(r2)  # {'is_nay_request': True, 'confidence': 0.95, 'explanation': "Contains capitalized 'NAY'"}

r3 = rejection_pattern.detect(title='AIWeb3 Chinese Unit proposal (爱Web3 中文社区提案)', content='Hello everyone in DotSama community, happy new year! This is DrCAO, I am Ex. community manager at Pa')
print(r3)  # {'is_nay_request': False, 'confidence': 0.9, 'explanation': "No indicators of a 'nay' vote request found"}
