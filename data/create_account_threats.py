"""
Create Account Threat Database
Extracts unique accounts and assigns threat levels and failed transaction counts
"""

import pandas as pd
import numpy as np

print("Creating Account Threat Database...")

# Load transaction data
df = pd.read_csv('output_1_to_10.csv')

print(f"Loaded {len(df)} transactions")

# Extract unique accounts from both sender and receiver
senders = df['nameOrig'].unique()
receivers = df['nameDest'].unique()
all_accounts = list(set(list(senders) + list(receivers)))

print(f"Found {len(all_accounts)} unique accounts")

# Create account threat database
account_data = []

for account in all_accounts:
    # Generate random threat level (0-100, higher = more suspicious)
    # Most accounts should have low threat (skewed distribution)
    threat_level = np.random.choice(
        [np.random.randint(0, 30),     # 70% chance: low threat (0-30)
         np.random.randint(30, 60),    # 20% chance: medium threat (30-60)
         np.random.randint(60, 100)],  # 10% chance: high threat (60-100)
        p=[0.7, 0.2, 0.1]
    )
    
    # Generate random failed transaction count (0-50)
    # Most accounts should have few failures
    failed_transactions = np.random.choice(
        [np.random.randint(0, 5),      # 80% chance: 0-5 failures
         np.random.randint(5, 15),     # 15% chance: 5-15 failures
         np.random.randint(15, 50)],   # 5% chance: 15-50 failures
        p=[0.8, 0.15, 0.05]
    )
    
    account_data.append({
        'account_id': account,
        'threat_level': threat_level,
        'failed_transactions': failed_transactions
    })

# Create DataFrame
account_df = pd.DataFrame(account_data)

# Save to CSV
account_df.to_csv('account_threats.csv', index=False)

print(f"\n✓ Created account_threats.csv with {len(account_df)} accounts")
print(f"\nThreat Level Statistics:")
print(f"  Mean: {account_df['threat_level'].mean():.2f}")
print(f"  Median: {account_df['threat_level'].median():.2f}")
print(f"  Min: {account_df['threat_level'].min()}")
print(f"  Max: {account_df['threat_level'].max()}")

print(f"\nFailed Transactions Statistics:")
print(f"  Mean: {account_df['failed_transactions'].mean():.2f}")
print(f"  Median: {account_df['failed_transactions'].median():.2f}")
print(f"  Min: {account_df['failed_transactions'].min()}")
print(f"  Max: {account_df['failed_transactions'].max()}")

# Show sample
print(f"\nSample accounts:")
print(account_df.head(10))

print("\n✓ Account threat database created successfully!")
