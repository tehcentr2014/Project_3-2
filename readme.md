## Content Marketing Assistant

![image](https://github.com/tehcentr2014/Project_3/assets/161617022/fbf18ada-a3e8-4887-a3a0-cc70c2fead05)

### Overview
The Content Marketing Assistant is a Python App designed to aid in the automatic generation of product descriptions using OpenAI Assistans API. This application simplifies the process by taking user-provided keywords and generating concise descriptions based on predefined criteria.

### Features
- **Keyword Input**: Users can input keywords related to the product for which they want to generate descriptions.
- **Duplicate Removal**: The application provides a functionality to remove duplicate keywords entered by the user.
- **Description Generation**: Using the provided keywords, the application generates product descriptions consisting of a title, bullet points, and a detailed description, adhering to specified character limits.
- **Streamlit Interface**: The application offers a user-friendly interface powered by Streamlit, making it accessible and easy to use.

### Installation
1. Clone the repository:

    ```bash
    git clone <repository-url>
    ```

2. Install the required dependencies:

    ```bash
    pip install -r requirements.txt
    ```

3. Set up OpenAI API access by creating a `.env` file in the root directory and adding your OpenAI API key:

    ```
    OPENAI_API_KEY=<your-openai-api-key>
    ```

### Usage
1. Run the application:

    ```bash
    python main.py
    ```

2. Access the application through the provided URL in your browser.
3. Follow the on-screen instructions to enter keywords and generate product descriptions.
4. Click the "Create description" button to initiate the description generation process.
5. Wait for the application to generate the description based on the provided keywords.
6. The generated description will be displayed on the interface.

### Acknowledgments
- This project utilizes the OpenAI API for natural language processing.
- Streamlit is used for creating the user interface.

