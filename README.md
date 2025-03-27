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

it