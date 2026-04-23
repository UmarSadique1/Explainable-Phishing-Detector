import os
import pandas as pd
import random

DATA_DIR = "data/email_dataset/raw"

MAX_ENRON_EMAILS = 400
MAX_EASY_HAM_EMAILS = 100
MAX_HARD_HAM_EMAILS = 100
MAX_SPAM_EMAILS = 700


def read_emails_from_folder(folder_path, label, max_emails):
    emails = []
    count = 0

    for root, _, files in os.walk(folder_path):
        for file in files:
            if count >= max_emails:
                break

            try:
                file_path = os.path.join(root, file)
                with open(file_path, "r", encoding="latin-1", errors="ignore") as f:
                    content = f.read().strip()

                    if content:
                        emails.append({
                            "text": content,
                            "label": label
                        })
                        count += 1
            except Exception:
                continue

        if count >= max_emails:
            break

    return emails


def build_dataset():
    dataset = []

    print("Loading Enron (Legitimate)...")
    dataset += read_emails_from_folder(
        os.path.join(DATA_DIR, "maildir"), 0, MAX_ENRON_EMAILS
    )

    print("Loading SpamAssassin Easy Ham...")
    dataset += read_emails_from_folder(
        os.path.join(DATA_DIR, "easy_ham"), 0, MAX_EASY_HAM_EMAILS
    )

    print("Loading SpamAssassin Hard Ham...")
    dataset += read_emails_from_folder(
        os.path.join(DATA_DIR, "hard_ham"), 0, MAX_HARD_HAM_EMAILS
    )

    print("Loading SpamAssassin Spam...")
    dataset += read_emails_from_folder(
        os.path.join(DATA_DIR, "spam"), 1, MAX_SPAM_EMAILS
    )

    random.shuffle(dataset)

    df = pd.DataFrame(dataset)

    print("\nDataset Summary:")
    print(df["label"].value_counts())

    output_path = "data/email_dataset/processed/emails.csv"
    os.makedirs("data/email_dataset/processed", exist_ok=True)
    df.to_csv(output_path, index=False)

    print(f"\nDataset saved to: {output_path}")


if __name__ == "__main__":
    build_dataset()