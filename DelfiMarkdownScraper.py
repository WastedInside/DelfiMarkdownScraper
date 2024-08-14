import os
import requests
from bs4 import BeautifulSoup
import html2text
import json
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox, scrolledtext
from datetime import datetime

# Function to append messages to the console and log file
def append_to_console(message, log_file):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted_message = f"[{now}] {message}\n"
    
    # Append to the console
    console.insert(tk.END, formatted_message)
    console.yview(tk.END)  # Auto-scroll to the end
    
    # Append to the log file
    with open(log_file, 'a', encoding='utf-8') as log:
        log.write(formatted_message)

# Function to scrape a single URL and save its content
def scrape_article(url, index, tag, class_name, save_dir, log_file):
    try:
        append_to_console(f"Scraping {url}...", log_file)
        response = requests.get(url)
        response.raise_for_status()  # Check for request errors

        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract the article content using the tag and class_name
        if tag and class_name:
            article_content = soup.find(tag, class_=class_name)
        else:
            article_content = soup.find('div', class_='article-content')  # Default if not specified

        if article_content:
            html_content = str(article_content)
        else:
            html_content = '<p>Article content not found.</p>'

        h2t = html2text.HTML2Text()
        h2t.ignore_links = False
        markdown_content = h2t.handle(html_content)

        # Define the path to the save directory
        file_path = os.path.join(save_dir, f'scraped_article_{index}.md')

        # Save the article content to a Markdown file
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(markdown_content)

        append_to_console(f"Article from {url} has been saved to {file_path}", log_file)
    except Exception as e:
        append_to_console(f"Failed to scrape {url}: {e}", log_file)

# Main function to process URLs from a file with site configurations
def process_urls(urls_file_path, config_file_path, save_dir):
    log_file = os.path.join(save_dir, 'log.txt')  # Log file path
    try:
        with open(config_file_path, 'r') as config_file:
            configs = json.load(config_file)

        with open(urls_file_path, 'r') as file:
            urls = file.readlines()

        for index, url in enumerate(urls, start=1):
            url = url.strip()
            if url:
                tag, class_name = configs.get("tag", None), configs.get("class_name", None)
                scrape_article(url, index, tag, class_name, save_dir, log_file)

        append_to_console("All articles have been saved successfully.", log_file)
    except Exception as e:
        append_to_console(f"An error occurred: {e}", log_file)

# GUI for selecting files and directories
def browse_file(entry):
    file_path = filedialog.askopenfilename()
    entry.delete(0, tk.END)
    entry.insert(0, file_path)

def browse_directory(entry):
    dir_path = filedialog.askdirectory()
    entry.delete(0, tk.END)
    entry.insert(0, dir_path)

def start_scraping():
    urls_file_path = urls_entry.get()
    config_file_path = config_entry.get()
    save_dir = save_entry.get()
    
    if not urls_file_path or not config_file_path or not save_dir:
        messagebox.showwarning("Input Error", "Please fill all fields.")
        return

    append_to_console("Starting the scraping process...", os.path.join(save_dir, 'log.txt'))
    process_urls(urls_file_path, config_file_path, save_dir)

# Create the main window
root = tk.Tk()
root.title("Delfi Markdown Scraper")

# URL text file
tk.Label(root, text="URLs File:").grid(row=0, column=0, padx=10, pady=5, sticky='e')
urls_entry = tk.Entry(root, width=50)
urls_entry.grid(row=0, column=1, padx=10, pady=5)
tk.Button(root, text="Browse", command=lambda: browse_file(urls_entry)).grid(row=0, column=2, padx=10, pady=5)

# Config file
tk.Label(root, text="Config File:").grid(row=1, column=0, padx=10, pady=5, sticky='e')
config_entry = tk.Entry(root, width=50)
config_entry.grid(row=1, column=1, padx=10, pady=5)
tk.Button(root, text="Browse", command=lambda: browse_file(config_entry)).grid(row=1, column=2, padx=10, pady=5)

# Save directory
tk.Label(root, text="Save Directory:").grid(row=2, column=0, padx=10, pady=5, sticky='e')
save_entry = tk.Entry(root, width=50)
save_entry.grid(row=2, column=1, padx=10, pady=5)
tk.Button(root, text="Browse", command=lambda: browse_directory(save_entry)).grid(row=2, column=2, padx=10, pady=5)

# Start Button
tk.Button(root, text="Start Scraping", command=start_scraping).grid(row=3, column=0, columnspan=3, pady=20)

# Console output
tk.Label(root, text="Console Output:").grid(row=4, column=0, columnspan=3, padx=10, pady=5)
console = scrolledtext.ScrolledText(root, width=80, height=20, wrap=tk.WORD)
console.grid(row=5, column=0, columnspan=3, padx=10, pady=10)
console.config(state=tk.NORMAL)

# Run the application
root.mainloop()
