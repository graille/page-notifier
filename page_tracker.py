"""
Page tracker module.

Provides functionality to fetch web pages and extract specific HTML elements.
"""

from bs4 import BeautifulSoup


def extract_element(html_content: str, selector_path: str) -> str:
    """
    Extract a specific HTML element from the page using a selector path.

    The selector path is a pipe-separated list of CSS selectors that are
    applied in sequence to navigate through the DOM (e.g., "#main|.content|#first").

    :param html_content: The raw HTML content of the page.
    :param selector_path: Pipe-separated CSS selectors (e.g., "#main|.content|#first").
                          If empty or None, returns the entire body content.
    :return: The HTML content of the selected element as a string.
    :raises ValueError: If the selector path is invalid or element not found.
    """
    soup = BeautifulSoup(html_content, "html.parser")

    # If no selector path, return the entire body
    if not selector_path or selector_path.strip() == "":
        body = soup.find("body")
        if body is None:
            return html_content
        return str(body)

    # Parse and apply each selector in sequence
    selectors = [s.strip() for s in selector_path.split("|") if s.strip()]

    current_element = soup
    for selector in selectors:
        found = current_element.select_one(selector)
        if found is None:
            raise ValueError(
                f"Element not found for selector '{selector}' in path '{selector_path}'"
            )
        current_element = found

    return str(current_element)


def normalize_html(html_content: str) -> str:
    """
    Normalize HTML content for comparison.

    Removes hidden elements (type="hidden"), extra whitespace and formats
    the HTML consistently to avoid false positives when comparing page content.

    :param html_content: The raw HTML content to normalize.
    :return: Normalized HTML string.
    """
    soup = BeautifulSoup(html_content, "html.parser")
    
    # Remove all elements with type="hidden"
    for hidden_element in soup.find_all(attrs={"type": "hidden"}):
        hidden_element.decompose()
    
    # Get text content and normalize whitespace
    return soup.get_text(separator=" ", strip=True)
