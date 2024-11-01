import requests


def fetch_page(url):
    try:
        # Send a GET request to the specified URL
        response = requests.get(url)
        response.raise_for_status()  # Check if the request was successful

        # Return the HTML content of the page
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None


def save_to_file(html_content, filename):
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(html_content)
    print(f"HTML content saved to {filename}")


def main():
    # Replace this URL with the desired webpage you want to extract
    url = 'https://www.wam.ae/ar/ai-search'  # Change to your target URL
    html_content = fetch_page(url)

    if html_content:
        # Save the fetched HTML content to a file
        save_to_file(html_content, 'output.html')


if __name__ == "__main__":
    main()
