# Coffee Cup Reader API

### Overview

The Coffee Cup Reader API is a FastAPI-based application that analyzes images of coffee cup traces to detect shapes and symbols, providing interpretations rooted in coffee cup reading culture. It leverages OpenCV for image processing, OpenAI's GPT-4o for symbol detection, and GPT-4 for generating meaningful readings. Users can upload one or more coffee cup images, and the API returns structured JSON results with detected symbols and a final narrative interpretation.

### Key Features

Image Processing: Trims coffee cup images using an ellipse and triangle mask.

Symbol Detection: Identifies overall shapes and tiny symbols using OpenAI's GPT-4o vision model.

Reading Generation: Aggregates results and generates a cohesive coffee cup reading using GPT-4o.

API-Driven: Provides a RESTful endpoint for easy integration.

### Use Cases

Personal Use: Individuals interested in coffee cup reading can upload images to receive automated interpretations.

Cultural Exploration: Researchers or enthusiasts studying coffee cup reading traditions can analyze patterns programmatically.

Commercial Application: Integration into a mobile app or website offering coffee cup reading as a novelty service.


### Folder Structure

coffee_cup_reader/

├── app/

│   ├── __init__.py              # Marks directory as a package

│   ├── main.py                  # FastAPI application entry point

│   ├── core/

│   │   ├── __init__.py

│   │   ├── config.py            # Configuration and environment variables

│   │   ├── image_processor.py   # Image trimming logic

│   │   └── symbol_analyzer.py   # Symbol detection logic

│   ├── models/

│   │   ├── __init__.py

│   │   └── schemas.py           # Pydantic models for request/response

│   └── utils/

│       ├── __init__.py

│       └── helpers.py           # Helper functions (e.g., base64 encoding)

├── .env                         # Environment variables (e.g., OPENAI_API_KEY)

├── requirements.txt             # Python dependencies

└── README.md                    # Project documentation (this file)



### Prerequisites


OpenAI API Key: Required for GPT-4o (image analysis) and GPT-4o (reading generation).

Execution Environment with Storage: A system (local machine or server) to:

Run Python 3.9+ and required libraries.

Store input images and output files (e.g., local filesystem or server disk).

Additional Recommendations

    Internet Connection: For OpenAI API calls.

    Sample Images: Coffee cup images (.jpeg, .jpg, or .png) for testing.

### Setup Instructions

1. Clone the Repository
git clone [<repository-url>](https://github.com/shubhamjangid510/coffe_cup.git)
cd coffee_cup_reader

2. Create a Virtual Environment

With these commands

    python -m venv venv

    source venv/bin/activate  # On Windows: venv\Scripts\activate

3. Install Dependencies

Run this command
    
    pip install -r requirements.txt

4. Configure Environment Variables

Create a .env file in the root directory with your OpenAI API key:

    OPENAI_API_KEY=your_openai_api_key_here

    USE_SERVER_STORAGE = "True" or "False" based on the requirement. 

5. Run the Application

With this command

    uvicorn app.main:app --reload

    Access the API at http://127.0.0.1:8000.

    Use the Swagger UI at http://127.0.0.1:8000/docs for interactive testing.


### Endpoints

### A. Upload Image

Uploads a coffee cup image for a specific reading ID and position.

Endpoint: POST /upload_image/

Request Parameters:

a. reading_id - string - Required - Unique identifier for the coffee cup reading
b. position - string Required - Position of the image (left, right, up, down, top)
c. file - UploadFile - Required - The image file to upload (PNG format enforced)

Constraints:

Only one file can be uploaded at a time.

Maximum file size: 15MB

Allowed positions: left, right, up, down, top

Example Response:
{
  "reading_id": "123456",
  "file_path": "s3://my-bucket/123456/image_left.png",
  "uploaded_count": 3,
  "message": "Image at position left uploaded successfully"
}

### B. Analyze Coffee Cup

Analyzes five coffee cup images for a given reading_id and generates a final reading.

Endpoint: POST /analyze_coffee_cup/
Method: POST

Request Parameters:

a. language - string - Required - Language for the analysis result
b. reading_id - string - Required - Unique identifier for the coffee cup reading


Example Response
{
  "readings": [
    {
      "Observation": "Tree",
      "Location": "top",
      "Strength": 7,
      "Meaning": "growth",
      "Image": "image_down.png"
    },
    {
      "Observation": "Tree",
      "Location": "bottom-left",
      "Strength": 7,
      "Meaning": "growth",
      "Image": "image_left.png"
    },
    {
      "Observation": "Mountain",
      "Location": "bottom-center",
      "Strength": 7,
      "Meaning": "obstacle",
      "Image": "image_right.png"
    },
    {
      "Observation": "Mountain",
      "Location": "bottom-center",
      "Strength": 9,
      "Meaning": "obstacles and challenges that offer growth",
      "Image": "image_top.png"
    },
    {
      "Observation": "mountain",
      "Location": "bottom-center",
      "Strength": 8,
      "Meaning": "obstacles and challenges, but also the potential for growth and achievement",
      "Image": "image_up.png"
    },
  
  ],
  "final_reading": "In the tapestry of your life, you find yourself at a junction where growth, challenges, and freedom intertwine to shape your path. As I peer into your cup, the symbols etched in its depths paint a vivid narrative of your past, present, and future.\n\nIn the recent past, the Tree at the bottom-left and the River flowing nearby suggest that you have been in a period of substantial personal growth and transformation. The strength of this tree, rooted and yet reaching upwards, indicates you've laid a solid foundation in your life. However, like a river that carves its path through the landscape, your journey has been one of movement and fluidity, reminding you that the journey itself is as significant as the destination.\n\nAt present, you stand at the center of a confluence of powerful energies. The Wave at the center hints that change is a constant presence in your life, urging you to adapt and to surf the tides of transformation with grace. Yet, alongside the wave, the imposing Mountain, strong and immovable, speaks to the formidable challenges you currently face. This mountain challenges you, yet its presence also offers a promise: any obstacle you overcome will lead to significant personal growth.\n\nAbove and beyond the mountain, a Bird soars at the top-center, bringing with it an air of freedom. This symbol encourages you to look beyond the immediate challenges, to find liberation in new perspectives, and be ready for incoming news that could alter your course. The bird's call harmonizes with the presence of another Tree at the top, affirming that growth and liberation can and will coexist in your journey.\n\nAs you peer into the future, you are met with a complex and yet promising landscape. Mountains appear once more at the bottom-center, their strength heightened, signifying enduring obstacles. However, these barriers are not to be feared; they are the very crucible of your potential success. Overcoming these trials will yield remarkable personal growth, akin to peaks that hold breathtaking vistas for those who dare to climb.\n\nIn tandem, a Crescent Moon glows in the upper-center, softly illuminating change and transitions. Its gentle light suggests that these upcoming shifts will not be abrupt but rather subtle and gradual, gently guiding you towards new horizons. A Bird, again, in this realm of the future, suggests that with these changes, you'll gain even greater freedom, carrying you into new perspectives and opportunities.\n\nEarth, air, water, and spirit—these elements weave the story of your life as it spreads before you. Held within these symbols is the promise of growth through challenge, freedom beyond confinement, and the continuous motion of your life's journey. Embrace the path ahead, for it holds the keys to your becoming."
}