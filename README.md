# DelfiMarkdownScraper - Article Scraper with GUI

This Python script allows you to scrape articles from a list of URLs and save the content in Markdown format. The script provides a simple graphical user interface (GUI) for selecting the URLs file, configuration file, and the directory where the scraped articles will be saved. Additionally, it logs all operations in a `log.txt` file in the same directory as the scraped articles.

## Features

- **Scrapes articles**: Extracts article content from a list of URLs.
- **Markdown conversion**: Converts HTML content to Markdown format.
- **GUI**: Provides an easy-to-use interface for selecting files and directories.
- **Console Output**: Displays real-time console output in the GUI.
- **Log File**: Saves console output to `log.txt` in the save directory.

## Requirements

- Python 3.x
- Required Python packages (listed in `requirements.txt`):
  - `requests`
  - `beautifulsoup4`
  - `html2text`
  - `tkinter` (included with Python on most systems)

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/WastedInside/DelfiMarkdownScraper.git
cd DelfiMarkdownScraper
```

### 2. Install Dependencies

#### For Unix-based Systems (Linux, macOS):

Run the installation script:

```bash
./install.sh
```

#### For Windows:

Run the installation script:

```batch
install.bat
```

Alternatively, you can manually install the required packages using pip:

```bash
pip install -r requirements.txt
```

## Usage

1. **Prepare Files**:
   - Create a text file containing the list of URLs you want to scrape (one URL per line).
   - Create a JSON configuration file specifying the HTML tag and class name for extracting the article content. Example:
     ```json
     {
         "tag": "div",
         "class_name": "article-content"
     }
     ```

2. **Run the Script**:
   - For Unix-based systems:
     ```bash
     python3 DelfiMarkdownScraper.py
     ```
   - For Windows:
     ```batch
     python DelfiMarkdownScraper.py
     ```

3. **Use the GUI**:
   - Use the "Browse" buttons to select the URLs file, configuration file, and save directory.
   - Click "Start Scraping" to begin the process.

4. **View Output**:
   - Scraped articles will be saved in Markdown format in the selected save directory.
   - The console output will be displayed in the GUI and saved to `log.txt` in the same directory.

## Example Configuration File

```json
{
    "tag": "div",
    "class_name": "article-body"
}
```

## Contributing

Feel free to fork this repository and submit pull requests. For major changes, please open an issue to discuss what you would like to change.
