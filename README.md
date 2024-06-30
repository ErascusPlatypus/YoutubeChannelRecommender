# Youtube Channel Recommender

## Project Description

The Youtube Channel Recommender is a web extension designed to enhance your YouTube browsing experience by providing personalized channel recommendations. Utilizing a combination of web scraping and a K-Nearest Neighbors (KNN) model, this tool helps users discover new channels that align with their interests.

### Key Features

1. **Automatic Detection and Recommendation:**
   - The extension automatically detects if a YouTube tab is open in your browser.
   - It extracts the channel name from the URL of the open YouTube tab.
   - Based on the extracted channel name, the extension uses a KNN model to provide a list of recommended channels.

2. **Manual Channel Entry:**
   - Users have the option to manually enter a YouTube channel name.
   - The extension will then generate and display a list of recommended channels similar to the entered channel.

### Technical Details

- **Web Scraping:**
  - The extension scrapes relevant data from YouTube to gather information about channels.
  
- **KNN Model:**
  - A pre-trained KNN model (`new_nearest_neighbors.joblib`) is used to find similar channels based on the data collected.
  
- **Flask Application:**
  - The backend server is built using Flask to handle API requests and serve the recommendations.

- **Dependencies:**
  - The project relies on several Python libraries for its functionality. These include:
    - `beautifulsoup4==4.12.3`
    - `Flask==3.0.3`
    - `Flask_Cors==4.0.1`
    - `joblib==1.4.2`
    - `pandas==2.2.2`
    - `pytube==15.0.0`
    - `Requests==2.32.3`
    - `scikit-learn==1.4.2`
    - `nltk==3.8.1`

### Installation and Setup

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/yourusername/youtube-channel-recommender.git
   cd youtube-channel-recommender
   ```

2. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Flask Server:**
   ```bash
   export FLASK_APP=app.py
   flask run
   ```

4. **Load the Extension in Your Browser:**
   - Follow the instructions for your specific browser to load the extension from the local directory.

### Usage

- **Automatic Recommendation:**
  - Open YouTube and navigate to a channel.
  - The extension will automatically detect the channel and display recommended channels.

- **Manual Recommendation:**
  - Enter a YouTube channel name in the extension's input field.
  - Click the "Get Recommendations" button to see a list of similar channels.
