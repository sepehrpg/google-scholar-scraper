import requests
from bs4 import BeautifulSoup
import pandas as pd
import tkinter as tk
from tkinter import filedialog
#should install openpyxl ****

def scrape_scholar_articles(query, num_pages, year_start=None, year_end=None, file_type="None", publisher_filter=None, citation_min=None):
    articles = []
    page = 0
    while page < num_pages:
        url = f"https://scholar.google.com/scholar?start={page * 10}&q={query}&hl=en&as_sdt=0,5"
        # Add filters
        if year_start:
            url += f"&as_ylo={year_start}"
        if year_end:
            url += f"&as_yhi={year_end}"
        if file_type:
            url += f"&as_filetype={file_type}"

        print(url)

        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        results = soup.find_all("div", class_="gs_ri")

        for result in results:
            # Extract title, authors, and link
            title = result.find("h3", class_="gs_rt").text
            authors_info = result.find("div", class_="gs_a").text
            link = result.find("a")["href"]

            # Extract citation count
            citation_info = result.find("div", class_="gs_fl").find_all("a")
            citation_text = [a.text for a in citation_info if "Cited by" in a.text]
            citation_count = int(citation_text[0].replace("Cited by ", "")) if citation_text else 0

            # Extract publisher or journal
            publisher = authors_info.split("-")[-1].strip() if "-" in authors_info else "Unknown"

            # Apply filters
            if publisher_filter and publisher_filter.lower() not in publisher.lower():
                continue
            if citation_min and citation_count < citation_min:
                continue

            articles.append({
                "Title": title,
                "Authors": authors_info,
                "Publisher": publisher,
                "Citations": citation_count,
                "Link": link
            })

        page += 1

    return articles

def save_to_excel(articles, filename):
    df = pd.DataFrame(articles)
    df.to_excel(filename, index=False)

def browse_folder():
    folder_path = filedialog.askdirectory()
    entry_folder.delete(0, tk.END)
    entry_folder.insert(tk.END, folder_path)

def scrape_articles():
    query = entry_query.get()
    num_pages = int(entry_pages.get())
    publisher_filter = entry_publisher.get()
    citation_min = int(entry_citation.get()) if entry_citation.get() else None

    articles = scrape_scholar_articles(
        query=query,
        num_pages=num_pages,
        year_start=2020,
        year_end=2024,
        publisher_filter=publisher_filter,
        citation_min=citation_min
    )

    folder_path = entry_folder.get()
    if folder_path:
        filename = f"{folder_path}/scholar_articles.xlsx"
    else:
        filename = "scholar_articles.xlsx"

    save_to_excel(articles, filename)
    label_status.config(text="Extraction complete. Data saved to scholar_articles.xlsx.")

# Create the main window
window = tk.Tk()
window.title("Google Scholar Scraper")
window.geometry("500x450")

# Create input fields and labels
label_query = tk.Label(window, text="Article Title or Keyword:")
label_query.pack()
entry_query = tk.Entry(window, width=60)
entry_query.pack()

label_pages = tk.Label(window, text="Number of Pages:")
label_pages.pack()
entry_pages = tk.Entry(window, width=60)
entry_pages.pack()

label_publisher = tk.Label(window, text="Filter by Publisher (optional):")
label_publisher.pack()
entry_publisher = tk.Entry(window, width=60)
entry_publisher.pack()

label_citation = tk.Label(window, text="Minimum Citation Count (optional):")
label_citation.pack()
entry_citation = tk.Entry(window, width=60)
entry_citation.pack()

label_folder = tk.Label(window, text="Output Folder (optional):")
label_folder.pack()
entry_folder = tk.Entry(window, width=60)
entry_folder.pack()

# Create browse button
button_browse = tk.Button(window, text="Browse", command=browse_folder)
button_browse.pack()

# Create extract button
button_extract = tk.Button(window, text="Extract Data", command=scrape_articles)
button_extract.pack()

# Create status label
label_status = tk.Label(window, text="")
label_status.pack()

# Run the main window loop
window.mainloop()
