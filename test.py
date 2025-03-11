#!/usr/bin/python3
import random
import numpy as np
import tensorflow as tf

def clean_text(txt):
    txt = txt.strip()
    txt = txt.encode("ascii", errors="ignore").decode()
    return txt

def random_extras():
    extras = ["!", "??", "...", "!!!", " [ERROR]", " (WRONG)", "", "", "", ""]
    return random.choice(extras)

def randomize_title(base_tuple):
    """
    base_tuple is (title_str, label_int).
    We'll randomize the text and return (modified_text, label_int) without CSV parsing.
    """
    raw_text, expected_label = base_tuple

    text = raw_text
    if "nay" in text.lower():
        if random.random() < 0.5:
            text = text.replace("nay", "NAY").replace("Nay", "NAY")
    if "vote" in text.lower():
        if random.random() < 0.5:
            text = text.replace("vote", "VOTE").replace("Vote", "VOTE")

    if random.random() < 0.3:
        text = random_extras() + " " + text
    if random.random() < 0.3:
        text = text + " " + random_extras()

    text = clean_text(text)
    return text.strip(), expected_label

def run_inference_test(model, base_tuples, num_tests, test_description):
    """
    base_tuples is a list of (text_str, label_int).
    We'll pick random samples, apply random transforms, and run inference.
    """
    test_samples = []
    for _ in range(num_tests):
        base_choice = random.choice(base_tuples)
        mod_text, exp_label = randomize_title(base_choice)
        test_samples.append((mod_text, exp_label))

    input_tensor = tf.constant([[ts[0]] for ts in test_samples], dtype=tf.string)

    logits = model.predict(input_tensor, batch_size=1, verbose=0)
    probs = tf.nn.softmax(logits, axis=1).numpy()

    print(f"\n=== {test_description} ===")
    for (text, exp_label), p in zip(test_samples, probs):
        pred_label = int(np.argmax(p))
        outcome = "PASS" if (pred_label == exp_label) else "FAIL"
        print(
            f"Title: {text}\n"
            f"Prob(class0)={p[0]:.4f}, Prob(class1)={p[1]:.4f} "
            f"=> Prediction={pred_label} | Expected={exp_label}, {outcome}\n"
        )

def main():
    model_path = "model.keras"
    print(f"Loading model from {model_path} ...")
    model = tf.keras.models.load_model(model_path, compile=False)
    print("Model loaded.\n")

    base_lines_1 = [
        ("Please vote nay", 1),
        ("Please vote nay, thank you!", 1),
        ("Vote nay on this", 1),
        ("Posted in error please vote nay", 1),
        ("Wrong amount vote nay", 1),
        ("Pre-Image error, vote NAY", 1),
        ("Error! Please vote NAY", 1),
        ("THIS PROPOSAL IS AN ERROR. PLEASE IGNORE: THE AMOUNT IS NOT CORRECT. PLEASE VOTE NAY.", 1),
        ("VOTE NAY - pre image error", 1),
        ("Wrong preimage - Please vote NAY", 1),
        ("Preimage removed - referendum revoked, VOTE NAY", 1),
        ("Please ignore - created in error, vote nay", 1),
        ("Mistake in pre-image - please vote NAY", 1),
        ("Please vote NAY - Resubmitted as #1014", 1),
        ("TEST Bounty Please Vote For NAY !", 1),
        ("Preimage unnoted, to be resubmitted [Please vote NAY]", 1),
        ("Wrong Call Data Please Vote NAY", 1),
        ("Proposal posted in error, kindly vote nay", 1),
        ("VOTE NAY. Wrong currency - resubmitting as stables", 1),
        ("Wrong track - please vote nay", 1),
        ("Error - vote NAY", 1),
        ("Please vote no, wrong preimage", 1)
    ]

    base_lines_0 = [
        ("Unbrick Nodle", 0),
        ("\"Polkadot @ SXSW 2023, Austin, Texas on March 12th-15th 2023\"", 0),
        ("Cancel Old Auctions Schedule - Replaced by New Schedule After OpenGov Inclusion", 0),
        ("Encointer Treasury Proposal (budget halving)", 0),
        ("Allocate DOT Loan for Use Amongst Cross-Ecosystem DeFi within the Cosmos Ecosystem", 0),
        ("RadiumBlock: Retroactive funding for High Performance Public Endpoint Service for Polkadot(Q4 2022 and Q1 2023)", 0),
        ("\"Nova Spektr Milestone 3 Proposal: Dynamic Derivations, WalletConnect v2, Proxy accounts, Cross-chain transfers, Fiat values, Ethereum address support, Staking improvements, Wallet details, App Store and Microsoft Store\"", 0),
        ("Magnet Proposal: Polkadot’s Smart Contract Docking Station using DOT as Gas Based on the PAYG Model", 0),
        ("Recognising Paradox's Contributions to Reject Gov 1 Proposals and Release Bonds", 0),
        ("[Whitelisted Caller] Referendum #122: Register KSM on Asset Hub", 0),
        ("Crypto-Friendly Substrate Scaffold Pallets for Every Parachains", 0),
        ("An Open Communication Layer For Polkadot", 0),
        ("Maintenance for the substrate-api-client Sep-23 to Dec-23", 0),
        ("\"Societal: Advanced Treasury, Governance and Member Management Systems for Decentralized Communities\"", 0),
        ("PolkaWorld Ops and Maintenance proposal：2023.9 - 2023.11", 0),
        ("Refunding CCTF's GOV1 Treasury Spend Deposit", 0),
        ("Refunding Radium Block's GOV1 Treasury Spend Deposit", 0),
        ("Refunding MIDL.DEV's GOV1 Treasury Spend Deposit", 0),
        ("Refunding Pink Node's GOV1 Treasury Spend Deposit", 0),
        ("Propose Curator for PAL Bounty", 0),
        ("[Whitelisted Caller] Referendum #110: Update Parachain Validation Config", 0),
        ("Polkasafe - Milestone 2 - Retroactive funding proposal", 0),
        ("SmallTipper", 0),
        ("LayerX - rollout parachain as Trustless Bridge between Polkadot and Ethereum.", 0),
        ("Community-Centric Blockchain Education: Dacade's Commitment to Polkadot's Growth via learning through sharing", 0),
        ("Proposal: OpenZeppelin x Polkadot Ecosystem Growth", 0),
        ("Polkadot journal: A Marketing Proposal for Polkadot/Kusama", 0),
        ("Milestone 3: Polkadot Hackathon Global Series 2023", 0),
        ("[Retroactive] Polytope Labs: ISMP Research & Development", 0),
        ("Milestone 3 Proposal: Polkadot x EasyA Hackathons at Harvard and in London (#60DaysOfPolkadot)", 0),
        ("A small tip for a staking rewards calculator", 0),
        ("Patron Milestones 2-7 Development", 0),
        ("POLKADOT INSIDER - 28 WEEKS OPERATION & GROWTH FUNDING (AUGUST 2023 - FEBRUARY 2024)", 0),
        ("Milestone 2 and 3 Payment Request – YieldBay: Polkadot’s yield farming dashboard", 0),
        ("=Artificial Intelligence for security monitoring on a network level", 0),
        ("Small tip for Polkadot community activation in Finland", 0),
        ("SmallTipper", 0),
        ("Infrastructure Funding for Polkadot Asset Hub - Migration of Kusama NFTs", 0),
        ("Specialized Learning Path of Polkadot Ecosystem for Devs", 0),
        ("Gosemble Phase 2 - a Framework for building Substrate-compatible Runtimes in Go (Parachains & Solochains)", 0),
        ("Proposal: Artificial Intelligence for security monitoring on a network level", 0),
        ("OnFinality Unified NFT API", 0),
        ("\"Substrate, XCM rust technical practice videos.\"", 0),
        ("DOT holders 🤝 & The Kusamarian 🤖❤️", 0),
        ("[Staking Admin] Referendum #84: Update System Collator Sets and Configurations", 0),
        ("SmallTipper", 0),
        ("OnFinality High Performance Public Infrastructure (Q2 2023)", 0),
        ("Bounty to back Apillon Web3 development platform as a common good infrastructure", 0),
        ("SmallTipper", 0),
        ("Blockops Network - Grant Proposal for the development of One-Click Parachain Deployment", 0),
        ("Smoldot development financing Q3/2023", 0),
        ("Polkashots.io Cloud Costs January-April 2023", 0),
        ("Rejecting Gov1.0 Treasury Proposals and Facilitating Bond Reimbursement where applicable", 0),
        ("A Polkadot Ecosystem App Store", 0),
        ("Wasm Smart Contracts Bounty #19", 0),
        ("Finsig SDK for Apple Products", 0),
        ("UI & Front-end for Asset Conversion pallet (referenda68) - Project Status Update - Delivery Completed", 0),
        ("\"Security Audit of trustless Ethereum 2.0 Light Client, developed as a Substrate Pallet\"", 0),
        ("Treasury Proposal by 727.ventures: Polkadot Wink", 0),
        ("Metadata for offline signers", 0),
        ("A small chatbot for the polkadot wiki", 0),
        ("A small tip for media representation", 0),
        ("[Whitelisted Caller] Referendum #58: Increase Parachain Validators to 250", 0),
        ("\"Rust, Substrate, ink! technical content for rust developers.\"", 0),
        ("Canceling Remaining Auctions and Introducing New Ones", 0),
        ("[TAKE TWO] Next revision of increasing nomination pool limits & commission", 0),
        ("25-minute contextual primer on Polkadot 2.0", 0),
        ("[Auction Admin] Referendum #53: Start an Auction", 0),
        ("DAO_Terminal: Enhancing User Involvement in Polkadot Governance", 0),
        ("Open HRMP Channels Between System Parachains", 0),
        ("\"GovernGoofed, a proposal to tackle 3 of the most challenging issues in OpenGov V1\"", 0),
        ("Part 2 of 2 request for 1100 DOT deposit reimbursement", 0),
        ("Part 1 of 2 request for 1100 DOT deposit reimbursement", 0),
        ("Approve Polkadot Assurance Legion Bounty", 0),
        ("\"Polkadot Hubs - Initiative case-study, education and support for future hubs (12 months period)\"", 0),
        ("Funded High Performance Public Infrastructure for the entire Polkadot Ecosystem (OnFinality)", 0),
        ("Treasury proposal for New Product Development & OpenGov Deployment", 0),
        ("Polkadot Relayers Incubator 2023", 0),
        ("Notifi Vote RE: #1767 Notifi - Communication & Notification Tooling for Polkadot's Broader Ecosystem", 0),
        ("Pinknode Public Endpoint for Polkadot in Q4 2022", 0),
        ("Next revision of increasing nomination pool limits & commission", 0),
        ("(Small tipper) Funding for AnimatedCrypto channel", 0),
        ("(Big Tipper) Small Funding for KryptosChain Media", 0),
        ("OneBlock The 2023 Polkadot Summer Hackathon proposal", 0),
        ("Polkadotters – retroactive and future funding of community powered media for Polkadot & Kusama ecosystem in 2022-2024", 0),
    ]

    run_inference_test(model, base_lines_1, 50, "TEST #1 (Should be Label=1)")
    run_inference_test(model, base_lines_0, 50, "TEST #2 (Should be Label=0)")

if __name__ == "__main__":
    main()
