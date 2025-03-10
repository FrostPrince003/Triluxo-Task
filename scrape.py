from bs4 import BeautifulSoup
import requests
import json

def get_course_details(course_url):
    """Get additional details from the course page"""
    try:
        response = requests.get(course_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        details = {}
        
        # Extract course description
        overview = soup.find('div', class_='courses-overview')
        if overview:
            # Get the description section
            description_section = overview.find('h3', string='Course Description')
            if description_section:
                # Get all text content after "Course Description" heading
                description = []
                current = description_section.find_next()
                
                while current and current.name != 'h3':
                    if current.name == 'p':
                        # Handle paragraphs
                        text = current.get_text(strip=True)
                        if text:
                            description.append(text)
                    elif current.name == 'br':
                        # Handle line breaks
                        description.append('')
                    elif current.name == 'ul':
                        # Handle bullet points
                        for li in current.find_all('li'):
                            description.append(f"• {li.get_text(strip=True)}")
                    current = current.find_next()
                
                details['course_description'] = '\n'.join(description)
            
            # Extract main features
            features_text = overview.get_text()
            if 'MAIN FEATURES OF THE PROGRAM:' in features_text:
                features_section = features_text.split('MAIN FEATURES OF THE PROGRAM:')[1]
                # Split by bullet points and clean up
                features = [
                    f.strip()
                    for f in features_section.split('•')
                    if f.strip() and not f.strip().startswith('MAIN FEATURES')
                ]
                details['main_features'] = features
        
        # Extract course info from the right sidebar
        info_list = soup.find('ul', class_='info')
        if info_list:
            info_items = info_list.find_all('li')
            for item in info_items:
                spans = item.find_all('span')
                if spans and len(spans) > 0:
                    key = spans[0].text.strip().replace(':', '').lower()
                    value = item.text.replace(spans[0].text, '').strip()
                    details[key] = value
        
        # Extract course image
        course_image = soup.find('div', class_='image')
        if course_image:
            img = course_image.find('img')
            if img:
                details['detail_image'] = img.get('src', '')
        
        return details
    except Exception as e:
        print(f"Error fetching course details: {str(e)}")
        return {}

def scrape_brainlox():
    # URL to scrape
    url = "https://brainlox.com/courses/category/technical"
    
    try:
        # Make a request to get the webpage content
        response = requests.get(url)
        response.raise_for_status()
        
        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all course cards/containers
        course_containers = soup.find_all('div', class_='single-courses-box')
        
        courses = []
        for course in course_containers:
            course_data = {}
            
            # Extract course image URL and alt text
            image_element = course.find('img')
            if image_element:
                course_data['image_url'] = image_element.get('src', '')
                course_data['image_alt'] = image_element.get('alt', '')
            
            # Extract course URL and title
            title_element = course.find('h3').find('a')
            if title_element:
                course_data['title'] = title_element.text.strip()
                course_url = 'https://brainlox.com' + title_element.get('href', '')
                course_data['course_url'] = course_url
                
                # Get detailed information from course page
                print(f"Fetching details for course: {course_data['title']}")
                course_data.update(get_course_details(course_url))
            
            # Extract short description from course card
            desc_element = course.find('p')
            if desc_element:
                course_data['short_description'] = desc_element.text.strip()
            
            # Extract price information
            price_element = course.find('span', class_='price-per-session')
            if price_element:
                price_text = price_element.text.replace('$', '').strip()
                course_data['price_per_session'] = float(price_text)
                
            # Extract price text (per session)
            price_text_element = course.find('span', class_='price-per-session-text')
            if price_text_element:
                course_data['price_text'] = price_text_element.text.strip()
            
            # Extract number of lessons
            lessons_element = course.find('li', text=lambda x: x and 'Lessons' in x)
            if lessons_element:
                lessons_text = lessons_element.text.strip()
                lessons_count = ''.join(filter(str.isdigit, lessons_text))
                course_data['lessons_count'] = int(lessons_count) if lessons_count else None
            
            courses.append(course_data)
        
        # Save the scraped data to a JSON file
        with open('courses_data.json', 'w', encoding='utf-8') as f:
            json.dump(courses, f, indent=4, ensure_ascii=False)
            
        print(f"Successfully scraped {len(courses)} courses!")
        return courses
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None

if __name__ == "__main__":
    scrape_brainlox()
