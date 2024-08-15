import os
import requests
from bs4 import BeautifulSoup
from markdownify import markdownify as md
import json
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
from datetime import datetime
import re

SETTINGS_FILE = 'scraper_settings.json'
untitled_article_count = 0

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_settings(settings):
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(settings, f)

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
def scrape_article(url, tag, class_name, title_tag, title_class, save_dir, log_file):
    global untitled_article_count
    try:
        append_to_console(f"Scraping {url}...", log_file)
        response = requests.get(url)
        response.raise_for_status()  # Check for request errors

        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract the article title
        if title_tag and title_class:
            title_element = soup.find(title_tag, class_=title_class)
        else:
            title_element = soup.find('h1')  # Default to first h1 if not specified

        if title_element and title_element.text.strip():
            article_title = title_element.text.strip()
        else:
            untitled_article_count += 1
            article_title = f"Untitled Article {untitled_article_count}"

        # Extract the article content using the tag and class_name
        if tag and class_name:
            article_content = soup.find(tag, class_=class_name)
        else:
            article_content = soup.find('div', class_='article-content')  # Default if not specified

        if article_content:
            html_content = str(article_content)
        else:
            html_content = '<p>Article content not found.</p>'

        # Convert HTML to Markdown using markdownify
        markdown_content = md(html_content, heading_style="ATX")

        # Create a valid filename from the article title
        valid_filename = re.sub(r'[^\w\-_\. ]', '_', article_title)
        valid_filename = valid_filename.replace(' ', '_')
        file_path = os.path.join(save_dir, f'{valid_filename}.md')

        # Ensure unique filename
        counter = 1
        while os.path.exists(file_path):
            file_path = os.path.join(save_dir, f'{valid_filename}_{counter}.md')
            counter += 1

        # Save the article content to a Markdown file
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(f"# {article_title}\n\n")  # Add the title as a header
            file.write(markdown_content)

        append_to_console(f"Article '{article_title}' from {url} has been saved to {file_path}", log_file)
    except Exception as e:
        append_to_console(f"Failed to scrape {url}: {e}", log_file)

# Main function to process URLs from a file with site configurations
def process_urls(urls_file_path, config, save_dir):
    global untitled_article_count
    untitled_article_count = 0  # Reset the counter at the start of each scraping session
    log_file = os.path.join(save_dir, 'log.txt')  # Log file path
    try:
        with open(urls_file_path, 'r') as file:
            urls = file.readlines()

        for url in urls:
            url = url.strip()
            if url:
                tag = config.get("content_tag")
                class_name = config.get("content_class")
                title_tag = config.get("title_tag")
                title_class = config.get("title_class")
                scrape_article(url, tag, class_name, title_tag, title_class, save_dir, log_file)

        append_to_console("All articles have been saved successfully.", log_file)
    except Exception as e:
        append_to_console(f"An error occurred: {e}", log_file)

# GUI for selecting files and directories
def browse_file(entry):
    file_path = filedialog.askopenfilename()
    if file_path:
        entry.delete(0, tk.END)
        entry.insert(0, file_path)
        save_settings({'last_urls_file': file_path, 'last_save_dir': save_entry.get(), 'last_config': config_var.get()})

def browse_directory(entry):
    dir_path = filedialog.askdirectory()
    if dir_path:
        entry.delete(0, tk.END)
        entry.insert(0, dir_path)
        save_settings({'last_urls_file': urls_entry.get(), 'last_save_dir': dir_path, 'last_config': config_var.get()})

# Function to load config files
def load_configs():
    config_dir = './configs'
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)
    config_files = [f for f in os.listdir(config_dir) if f.endswith('.json')]
    return {f: json.load(open(os.path.join(config_dir, f))) for f in config_files}

# Modified start_scraping function
def start_scraping():
    urls_file_path = urls_entry.get()
    config = configs[config_var.get()]
    save_dir = save_entry.get()
    
    if not urls_file_path or not config or not save_dir:
        messagebox.showwarning("Input Error", "Please fill all fields.")
        return

    save_settings({'last_urls_file': urls_file_path, 'last_save_dir': save_dir, 'last_config': config_var.get()})

    log_file = os.path.join(save_dir, 'log.txt')
    append_to_console("Starting the scraping process...", log_file)
    process_urls(urls_file_path, config, save_dir)

# Create the main window
root = tk.Tk()
root.title("Delfi Markdown Scraper")
root.geometry("600x500")  # Set a fixed size for the window

# Create a main frame
main_frame = ttk.Frame(root, padding="10")
main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

# Load saved settings
settings = load_settings()

# URL text file
ttk.Label(main_frame, text="URLs File:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
urls_entry = ttk.Entry(main_frame, width=50)
urls_entry.grid(row=0, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
urls_entry.insert(0, settings.get('last_urls_file', ''))
ttk.Button(main_frame, text="Browse", command=lambda: browse_file(urls_entry)).grid(row=0, column=2, padx=5, pady=5)

# Config dropdown
ttk.Label(main_frame, text="Config:").grid(row=1, column=0, padx=5, pady=5, sticky='e')
configs = load_configs()
config_var = tk.StringVar(root)
if configs:
    config_var.set(settings.get('last_config', next(iter(configs))))
else:
    config_var.set("No configs found")
config_dropdown = ttk.Combobox(main_frame, textvariable=config_var, values=list(configs.keys()), state="readonly", width=47)
config_dropdown.grid(row=1, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))

# Save directory
ttk.Label(main_frame, text="Save Directory:").grid(row=2, column=0, padx=5, pady=5, sticky='e')
save_entry = ttk.Entry(main_frame, width=50)
save_entry.grid(row=2, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
save_entry.insert(0, settings.get('last_save_dir', ''))
ttk.Button(main_frame, text="Browse", command=lambda: browse_directory(save_entry)).grid(row=2, column=2, padx=5, pady=5)

# Start Button
ttk.Button(main_frame, text="Start Scraping", command=start_scraping).grid(row=3, column=0, columnspan=3, pady=20)

# Console output
ttk.Label(main_frame, text="Console Output:").grid(row=4, column=0, columnspan=3, padx=5, pady=5)
console = scrolledtext.ScrolledText(main_frame, width=70, height=15, wrap=tk.WORD)
console.grid(row=5, column=0, columnspan=3, padx=5, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))
console.config(state=tk.NORMAL)

# Configure row and column weights
for i in range(6):
    main_frame.rowconfigure(i, weight=1)
for i in range(3):
    main_frame.columnconfigure(i, weight=1)

# Run the application
root.mainloop()