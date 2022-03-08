# Import Splinter and BeautifulSoup
from splinter import Browser
from bs4 import BeautifulSoup as soup
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import datetime as dt

def scrape_all():
    # Initiate headless driver for deployment
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=True)

    news_title, news_paragraph = mars_news(browser)

    # Run all scraping functions and store results in dictionary
    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "last_modified": dt.datetime.now(),
        "hemispheres": hemispheres(browser)
    }

    # Stop webdriver and return data
    browser.quit()
    return data


def mars_news(browser):
    # Visit the mars nasa news site
    url = 'https://redplanetscience.com/'
    browser.visit(url)
    # Optional delay for loading the page
    browser.is_element_present_by_css('div.list_text', wait_time=1)

    html = browser.html
    news_soup = soup(html, 'html.parser')
    
    # Add try/except for error handling
    try:
        slide_elem = news_soup.select_one('div.list_text')

        # Use the parent element to find the first `a` tag and save it as `news_title`
        news_title = slide_elem.find('div', class_='content_title').get_text()

        # Use the parent element to find the paragraph text
        news_p = slide_elem.find('div', class_='article_teaser_body').get_text()
    
    except AttributeError:
        return None, None

    return news_title, news_p


# ### Featured Images

def featured_image(browser):

    # Visit URL
    url = 'https://spaceimages-mars.com/'
    browser.visit(url)

    # Find and click the full image button
    full_image_elem = browser.find_by_tag('button')[1]
    full_image_elem.click()

    # Parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')

    try:
        # Find the relative image url
        img_url_rel = img_soup.find('img', class_='fancybox-image').get('src')

    except AttributeError:
        return None

    # Use the base URL to create an absolute URL
    img_url = f'https://spaceimages-mars.com/{img_url_rel}'

    return img_url


# ## Mars Facts

def mars_facts():
    
    try:
        # use 'read_html" to scrape the facts table into a dataframe
        df = pd.read_html('https://data-class-mars-facts.s3.amazonaws.com/Mars_Facts/index.html')[0]
    
    except BaseException:
        return None
    
    # Assign columns and set index of dataframe
    df.columns = ['Description', 'Mars', 'Earth']
    df.set_index('Description', inplace=True)
    
    # Convert dataframe into HTML format, add bootstrap
    return df.to_html(classes = "table table-striped")

# Function for collecting hemisphere images and titles

def hemispheres(browser):
    # Use browser to visit the URL 
    url = 'https://marshemispheres.com/'
    browser.visit(url)

    # Create a list to hold the images and titles.
    hemisphere_image_urls = []

    # Write code to retrieve the image urls and titles for each hemisphere.
    html = browser.html
    img_soup = soup(html, 'html.parser')


    for i in range(4):
        hemispheres = {}
        browser.find_by_css('a.product-item h3')[i].click()
        image_url = browser.find_link_by_text('Sample')['href']
        image_title = browser.find_by_css('h2.title').text
        hemispheres['image_url'] = image_url
        hemispheres['image_title'] = image_title
        hemisphere_image_urls.append(hemispheres)
        browser.back()


    # Return the list that holds the dictionary of each image url and title.
    return hemisphere_image_urls



if __name__ == "__main__":
    # If running as script, print scraped data
    print(scrape_all())


