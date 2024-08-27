import os
import requests
from bs4 import BeautifulSoup
from markdownify import markdownify as md
import json
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
from datetime import datetime
import re
from urllib.parse import urlparse
import subprocess

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
def append_to_console(message, log_file, message_type='info', console_only=False):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted_message = f"[{now}] {message}\n"
    
    # Append to the console with color coding
    if message_type == 'success':
        console.tag_config('success', foreground='green')
        console.insert(tk.END, formatted_message, 'success')
    elif message_type == 'error':
        console.tag_config('error', foreground='red')
        console.insert(tk.END, formatted_message, 'error')
    else:
        console.insert(tk.END, formatted_message)
    
    console.yview(tk.END)  # Auto-scroll to the end
    
    # Append to the log file if not console_only
    if not console_only:
        with open(log_file, 'a', encoding='utf-8') as log:
            log.write(formatted_message)

def get_domain(url):
    return urlparse(url).netloc

# Function to scrape a single URL and save its content
def scrape_article(url, tag, class_name, title_tag, title_class, subtitle_tag, subtitle_class, save_dir, log_file):
    global untitled_article_count
    try:
        domain = get_domain(url)
        append_to_console(f"Scraping {domain}...", log_file, console_only=True)
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

        # Extract the subtitle (if configured)
        subtitle = ""
        if subtitle_tag and subtitle_class:
            subtitle_element = soup.find(subtitle_tag, class_=subtitle_class)
            if subtitle_element:
                subtitle = subtitle_element.text.strip()

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
            file.write(f"# {article_title}\n\n")
            if subtitle:
                file.write(f"## {subtitle}\n\n")
            file.write(markdown_content)

        append_to_console(f"Article '{article_title}' has been saved", log_file, 'success', console_only=True)
        append_to_console(f"Article '{article_title}' from {url} has been saved to {file_path}", log_file, 'success')
    except Exception as e:
        append_to_console(f"Failed to scrape {domain}", log_file, 'error', console_only=True)
        append_to_console(f"Failed to scrape {url}: {e}", log_file, 'error')


        # Load the configuration file based on the domain

def load_config_for_domain(domain):
    # Remove 'www.' if present and replace '.' with '_'
    config_filename = domain.replace('www.', '').replace('.', '_') + '.json'
    config_path = f"./configs/{config_filename}"
    if os.path.exists(config_path):
        with open(config_path, 'r') as file:
            return json.load(file)
    else:
        return None


# Main function to process URLs from a file with site configurations
def process_urls(urls_file_path, save_dir):
    global untitled_article_count
    untitled_article_count = 0  # Reset the counter at the start of each scraping session
    log_file = os.path.join(save_dir, 'log.txt')  # Log file path
    try:
        with open(urls_file_path, 'r') as file:
            urls = file.readlines()

        for url in urls:
            url = url.strip()
            if url:
                domain = get_domain(url)
                append_to_console(f"Processing: {domain}", log_file, console_only=True)
                append_to_console(f"Processing URL: {url}", log_file)
                append_to_console(f"Extracted domain: {domain}", log_file)
                config = load_config_for_domain(domain)
                if config:
                    append_to_console(f"Config loaded for {domain}", log_file, 'success')
                    tag = config.get("content_tag")
                    class_name = config.get("content_class")
                    title_tag = config.get("title_tag")
                    title_class = config.get("title_class")
                    subtitle_tag = config.get("subtitle_tag")
                    subtitle_class = config.get("subtitle_class")
                    scrape_article(url, tag, class_name, title_tag, title_class, subtitle_tag, subtitle_class, save_dir, log_file)
                else:
                    append_to_console(f"No configuration found for: {domain}", log_file, 'error', console_only=True)
                    append_to_console(f"No configuration file found for domain: {domain}", log_file, 'error')
            else:
                append_to_console("Empty URL encountered", log_file)

        append_to_console("All articles have been saved successfully.", log_file, 'success')
    except Exception as e:
        append_to_console(f"An error occurred: {e}", log_file, 'error')

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
    save_dir = save_entry.get()
    
    if not urls_file_path or not save_dir:
        messagebox.showwarning("Input Error", "Please fill all fields.")
        return

    save_settings({'last_urls_file': urls_file_path, 'last_save_dir': save_dir})

    log_file = os.path.join(save_dir, 'log.txt')
    append_to_console("Starting the scraping process...", log_file)
    process_urls(urls_file_path, save_dir)

def clear_console():
    console.delete(1.0, tk.END)
    append_to_console("Console cleared.", log_file, 'info', console_only=True)

def open_save_location():
    save_dir = save_entry.get()
    if os.path.exists(save_dir):
        if os.name == 'nt':  # For Windows
            os.startfile(save_dir)
        elif os.name == 'posix':  # For macOS and Linux
            subprocess.call(('open', save_dir))
        else:
            append_to_console("Unsupported operating system for opening folders.", log_file, 'error')
    else:
        append_to_console("Save directory does not exist.", log_file, 'error')

# Create the main window

root = tk.Tk()
root.title("Delfi Markdown Scraper")
root.geometry("600x550")  # Increased height to accommodate new buttons

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

# Config info label (replace the dropdown)
ttk.Label(main_frame, text="Configurations:").grid(row=1, column=0, padx=5, pady=5, sticky='e')
configs = load_configs()
config_count = len(configs)
config_info = f"{config_count} configurations loaded dynamically."
ttk.Label(main_frame, text=config_info).grid(row=1, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))

# Save directory
ttk.Label(main_frame, text="Save Directory:").grid(row=2, column=0, padx=5, pady=5, sticky='e')
save_entry = ttk.Entry(main_frame, width=50)
save_entry.grid(row=2, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
save_entry.insert(0, settings.get('last_save_dir', ''))
ttk.Button(main_frame, text="Browse", command=lambda: browse_directory(save_entry)).grid(row=2, column=2, padx=5, pady=5)

# Start Button
ttk.Button(main_frame, text="Start Scraping", command=start_scraping).grid(row=3, column=0, columnspan=3, pady=10)

# Clear Console and Open Save Location buttons
button_frame = ttk.Frame(main_frame)
button_frame.grid(row=4, column=0, columnspan=3, pady=10)

ttk.Button(button_frame, text="Clear Console", command=clear_console).grid(row=0, column=0, padx=5)
ttk.Button(button_frame, text="Open Save Location", command=open_save_location).grid(row=0, column=1, padx=5)

# Console output
ttk.Label(main_frame, text="Console Output:").grid(row=5, column=0, columnspan=3, padx=5, pady=5)
console = scrolledtext.ScrolledText(main_frame, width=70, height=15, wrap=tk.WORD)
console.grid(row=6, column=0, columnspan=3, padx=5, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))
console.config(state=tk.NORMAL)
console.tag_config('success', foreground='green')
console.tag_config('error', foreground='red')

# Configure row and column weights
for i in range(7):  # Increased to 7 to account for the new row
    main_frame.rowconfigure(i, weight=1)
for i in range(3):
    main_frame.columnconfigure(i, weight=1)

# Run the application
root.mainloop()
