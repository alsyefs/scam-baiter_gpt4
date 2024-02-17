import os
import json
from shutil import copy2
from datetime import datetime
from tqdm import tqdm
from globals import (
    BASE_DIR, MAIL_SAVE_DIR, MAIL_ARCHIVE_DIR, UNIQUE_EMAIL_QUEUED,
    UNIQUE_EMAIL_QUEUED_DUPLICATE, EMAIL_ARCHIVED_CLEANED_DIR,
    EMAIL_ARCHIVED_CLEANED_CONVERSATIONS_DIR, ADDR_SOL_PATH,
    EMAIL_ARCHIVED_CLEANED_CONVERSATIONS_DIR_MOST_CONVERSATIONS,
    EMAIL_ARCHIVED_CLEANED_CONVERSATIONS_DIR_LONGEST_CONVERSATIONS,
    MAILGUN_DOMAIN_NAME, EMAIL_ARCHIVED_REPORT, EMAILS_REPORT_DIR,
    EMAIL_CONVERSATIONS_REPORT_CSV
)
def get_sol_from_addr_sol_path(email_to, email_from):
    with open(ADDR_SOL_PATH, 'r') as f:
        addr_sol_data = json.load(f)
    chat_1 = 'gpt-4-Chat1'
    chat_2 = 'gpt-4-Chat2'
    result = None
    for key, value in addr_sol_data.items():
        if key.lower() == email_to.lower():
            if value.get('sol') == 'Chat1':
                result = chat_1
            elif value.get('sol') == 'Chat2':
                result = chat_2
        elif key.lower() == email_from.lower():
            if value.get('sol') == 'Chat1':
                result = chat_1
            elif value.get('sol') == 'Chat2':
                result = chat_2
    if result:
        return result

def check_duplicate_queued_emails(hide_emails=True):
    os.makedirs(EMAILS_REPORT_DIR, exist_ok=True)
    email_set = set()
    email_dup_set = set()
    email_count = 0
    total_files_to_process = sum(1 for filename in os.listdir(MAIL_SAVE_DIR) if filename.endswith(".json"))
    with tqdm(total=total_files_to_process) as progress_bar:
        for filename in os.listdir(MAIL_SAVE_DIR):
            progress_bar.update(1)
            if filename.endswith(".json"):
                file_path = os.path.join(BASE_DIR, "emails", "queued", filename)
                with open(file_path, "r", encoding="utf8") as f:
                    email = json.load(f)
                    email_count += 1
                    if email["from"] in email_set:
                        email_dup_set.add(email["from"])
                    else:
                        email_set.add(email["from"])
    with open(EMAIL_ARCHIVED_REPORT, "w", encoding="utf-8") as file:
            file.write(f"Number of queued emails to be interacted with: ({email_count}).\n")
            print(f"Number of queued emails to be interacted with: ({email_count}).")
            file.write(f"Number of duplicate queued emails to be interacted with: ({len(email_dup_set)}).\n")
            print(f"Number of duplicate queued emails to be interacted with: ({len(email_dup_set)}).")
            file.write(f"Number of unique queued emails to be interacted with: ({len(email_set)}).\n")
            print(f"Number of unique queued emails to be interacted with: ({len(email_set)}).")
    if not hide_emails:
        with open(UNIQUE_EMAIL_QUEUED, "w", encoding="utf8") as f:
            total_files_to_process = sum(1 for email in email_set)
            with tqdm(total=total_files_to_process) as progress_bar:
                for email in email_set:
                    progress_bar.update(1)
                    f.write(email + "\n")
        with open(UNIQUE_EMAIL_QUEUED_DUPLICATE, "w", encoding="utf8") as f:
            total_files_to_process = sum(1 for email in email_dup_set)
            with tqdm(total=total_files_to_process) as progress_bar:
                for email in email_dup_set:
                    progress_bar.update(1)
                    f.write(email + "\n")

def clean_and_sort_conversations(source_directory, output_directory,
                                 conversations_directory,
                                 most_conversations_directory,
                                 longest_conversations_directory,
                                 report_file,
                                 hide_emails=True):
    os.makedirs(output_directory, exist_ok=True)
    os.makedirs(conversations_directory, exist_ok=True)
    os.makedirs(most_conversations_directory, exist_ok=True)
    os.makedirs(longest_conversations_directory, exist_ok=True)
    os.makedirs(EMAILS_REPORT_DIR, exist_ok=True)
    conversation_counts = {}
    total_files_to_process = sum(1 for filename in os.listdir(source_directory) if filename.endswith(".json") and not filename.endswith("_history.json"))
    file_count = 0
    total_days_scambaiting = 0
    with tqdm(total=total_files_to_process) as progress_bar:
        for filename in os.listdir(source_directory):
            if filename.endswith(".json") and not filename.endswith("_history.json"):
                progress_bar.update(1)
                file_count += 1
                file_path = os.path.join(source_directory, filename)
                if hide_emails:
                        filename = "scammer" + "_" + str(file_count) + ".json"
                conversations = []
                unique_emails = set()
                conversation_counter = 0
                with open(file_path, 'r', encoding='utf-8') as file:
                    strategy_name = None
                    for line in file:
                        try:
                            email = json.loads(line)
                            email['time'] = datetime.fromtimestamp(email['time']).strftime('%Y-%m-%d %H:%M:%S')
                            if conversation_counter == 0 or conversation_counter == 1:
                                first_email_time = email['time']
                            last_email_time = email['time']
                            email['days_from_first_conversation'] = (datetime.strptime(last_email_time, '%Y-%m-%d %H:%M:%S') - datetime.strptime(first_email_time, '%Y-%m-%d %H:%M:%S')).days
                            if email['days_from_first_conversation'] > total_days_scambaiting:
                                total_days_scambaiting = email['days_from_first_conversation']
                            if not strategy_name or strategy_name == 'None':
                                strategy_name = get_sol_from_addr_sol_path(email["to"], email["from"])
                            email["startegy"] = strategy_name
                            if not strategy_name:
                                email["startegy"] = 'None'
                            serialized_email = json.dumps({key: email[key] for key in ["from", "to", "subject", "body", "direction"]}, sort_keys=True)
                            if serialized_email not in unique_emails:
                                email["conversation_counter"] = str(conversation_counter)
                                if hide_emails:
                                    email.pop('time')
                                    if "@"+MAILGUN_DOMAIN_NAME in email["from"]:
                                        email["from"] = "baiter" + "_" + str(file_count)
                                    else:
                                        if "CRAWLER" not in email["from"]:
                                            email["from"] = "scammer" + "_" + str(file_count)
                                    if "@"+MAILGUN_DOMAIN_NAME in email["to"]:
                                        email["to"] = "baiter" + "_" + str(file_count)
                                    else:
                                        if "CRAWLER" not in email["to"]:
                                            email["to"] = "scammer" + "_" + str(file_count)
                                conversation_counter += 1
                                unique_emails.add(serialized_email)
                                email_body = email["body"]
                                email.pop("body")
                                email["body"] = email_body
                                conversations.append(email)
                        except json.JSONDecodeError as e:
                            print(f"Error decoding JSON in {filename}: {e}")
                if conversations:
                    cleaned_file_path = os.path.join(output_directory, filename)
                    with open(cleaned_file_path, 'w', encoding='utf-8') as cleaned_file:
                        json.dump(conversations, cleaned_file, ensure_ascii=False, indent=4)
                    conversation_counts[filename] = len(conversations)
    if conversation_counts:
        files_with_more_than_one_conversation = 0
        total_conversations = 0
        conversations_report = {}
        for filename, count in conversation_counts.items():
            if count > 2:
                files_with_more_than_one_conversation += 1
                total_conversations += count
                source_path = os.path.join(output_directory, filename)
                destination_path = os.path.join(conversations_directory, filename)
                copy2(source_path, destination_path)
                with open(os.path.join(output_directory, filename), 'r', encoding='utf-8') as file:
                    emails = json.load(file)
                days_from_first_conversation = emails[-1]['days_from_first_conversation']
                conversation_counter = emails[-1]['conversation_counter']
                scambaiting_strategy = emails[-1]['startegy'] 
                conversations_report[filename] = {'days_from_first_conversation': days_from_first_conversation,
                                                  'number_of_conversations': conversation_counter,
                                                  'strategy': scambaiting_strategy}
        most_conversations = {k: v for k, v in sorted(conversations_report.items(), key=lambda item: item[1]['number_of_conversations'], reverse=True)}
        longest_conversations_in_days = {k: v for k, v in sorted(conversations_report.items(), key=lambda item: item[1]['days_from_first_conversation'], reverse=True)}
        strategy_counts = {}
        for conversation in conversations_report.values(): # Initialize counts for each strategy
            if 'None' not in conversation['strategy']:
                strategy = conversation['strategy']
                if strategy not in strategy_counts:
                    strategy_counts[strategy] = 0
        for conversation in conversations_report.values(): # Increment counts for each strategy found
            if 'None' not in conversation['strategy']:
                strategy = conversation['strategy']
                strategy_counts[strategy] += 1
        with open(report_file, "a", encoding="utf-8") as file:
            for strategy, count in strategy_counts.items():
                file.write(f"Strategy ({strategy}) was used with ({count}) conversation threads.\n")
                print(f"Strategy ({strategy}) was used with ({count}) conversation threads.")
            file.write(f"Number of conversation threads scammers: ({files_with_more_than_one_conversation}).\n")
            print(f"\nNumber of conversation threads scammers: ({files_with_more_than_one_conversation}).")
            file.write(f"Total number of conversations with all scammers who have engaged in more than one conversation: ({total_conversations}).\n")
            print(f"Total number of conversations with all scammers who have engaged in more than one conversation: ({total_conversations}).")
            file.write(f"Total number of days scambaiting from the first conversation with a scammer: ({total_days_scambaiting}).\n")
            print(f"Total number of days scambaiting from the first conversation with a scammer: ({total_days_scambaiting}).")
            file.write(f"\n*** Top 10 most conversations with scammers: \n")
            print(f"\n*** Top 10 most conversations with scammers:")
            counter = 0
            for filename, days in list(most_conversations.items())[:10]: # top 10 most conversations
                counter+=1
                file.write(f"{counter}. Conversations with ({filename.replace('.json', '')}) took ({days['days_from_first_conversation']}) days and had ({days['number_of_conversations']}) conversations using ({days['strategy']}).\n")
                print(f"{counter}. Conversations with ({filename.replace('.json', '')}) took ({days['days_from_first_conversation']}) days and had ({days['number_of_conversations']}) conversations using ({days['strategy']}).")
                source_path = os.path.join(output_directory, filename)
                destination_path = os.path.join(most_conversations_directory, filename)
                copy2(source_path, destination_path)
            file.write(f"\n*** Top 10 longest conversations with scammers: \n")
            print(f"\n*** Top 10 longest conversations with scammers:")
            counter = 0
            for filename, days in list(longest_conversations_in_days.items())[:10]: # top 10 longest conversations
                counter+=1
                file.write(f"{counter}. Conversations with ({filename.replace('.json', '')}) took ({days['days_from_first_conversation']}) days and had ({days['number_of_conversations']}) conversations using ({days['strategy']}).\n")
                print(f"{counter}. Conversations with ({filename.replace('.json', '')}) took ({days['days_from_first_conversation']}) days and had ({days['number_of_conversations']}) conversations using ({days['strategy']}).")
                source_path = os.path.join(output_directory, filename)
                destination_path = os.path.join(longest_conversations_directory, filename)
                copy2(source_path, destination_path)
            counter = 0
            file.write(f"\n*** All conversations with scammers: \n")
            for filename, days in conversations_report.items():
                counter+=1
                file.write(f"{counter}. Conversations with ({filename.replace('.json', '')}) took ({days['days_from_first_conversation']}) days and had ({days['number_of_conversations']}) conversations using ({days['strategy']}).\n")
        counter = 0
        with open(EMAIL_CONVERSATIONS_REPORT_CSV, "w", encoding="utf-8") as file:
            file.write("n, scammer,conversation_days,number_of_conversations,strategy\n")
            for filename, days in conversations_report.items():
                counter+=1
                file.write(f"{counter}, {filename.replace('.json', '')},{days['days_from_first_conversation']},{days['number_of_conversations']}, {days['strategy']}\n")
    else:
        print("No files with valid conversations were found.")

if __name__ == "__main__":
    print(f"Running...")
    hide_emails = True
    print(f"Checking duplicate emails in ({os.path.relpath(MAIL_SAVE_DIR, BASE_DIR)})...")
    check_duplicate_queued_emails(hide_emails=hide_emails)
    print(f"Completed checking duplicate emails. Stored unique and duplicate emails in ({os.path.relpath(UNIQUE_EMAIL_QUEUED, BASE_DIR)}) and ({os.path.relpath(UNIQUE_EMAIL_QUEUED_DUPLICATE, BASE_DIR)}) respectively.")

    print(f"Reading files in ({os.path.relpath(MAIL_ARCHIVE_DIR, BASE_DIR)}) for cleaning and sorting conversations...")
    clean_and_sort_conversations(MAIL_ARCHIVE_DIR,
                                 EMAIL_ARCHIVED_CLEANED_DIR,
                                 EMAIL_ARCHIVED_CLEANED_CONVERSATIONS_DIR,
                                 EMAIL_ARCHIVED_CLEANED_CONVERSATIONS_DIR_MOST_CONVERSATIONS,
                                 EMAIL_ARCHIVED_CLEANED_CONVERSATIONS_DIR_LONGEST_CONVERSATIONS,
                                 EMAIL_ARCHIVED_REPORT,
                                 hide_emails=hide_emails)
    print(f"\n1. Copied the files from ({os.path.relpath(MAIL_ARCHIVE_DIR, BASE_DIR)}), cleaned them, sorted them, added startegy, then made another copy to ({os.path.relpath(EMAIL_ARCHIVED_CLEANED_DIR, BASE_DIR)}) without affecting the original files.")
    print(f"2. Created a copy of conversations with more than one conversation in ({os.path.relpath(EMAIL_ARCHIVED_CLEANED_CONVERSATIONS_DIR, BASE_DIR)}).")
    print(f"3. Created a copy of top 10 conversations with the maximum number of conversations in ({os.path.relpath(EMAIL_ARCHIVED_CLEANED_CONVERSATIONS_DIR_MOST_CONVERSATIONS, BASE_DIR)}).")
    print(f"4. Created a copy of top 10 conversations with the longest duration in days in ({os.path.relpath(EMAIL_ARCHIVED_CLEANED_CONVERSATIONS_DIR_LONGEST_CONVERSATIONS, BASE_DIR)}).")
    print(f"5. Created a report in ({os.path.relpath(EMAIL_ARCHIVED_REPORT, BASE_DIR)}).")
    print(f"6. Created a CSV report in ({os.path.relpath(EMAIL_CONVERSATIONS_REPORT_CSV, BASE_DIR)}).")
    print(f"Done.")
