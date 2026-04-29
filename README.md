# LinkedIn Post Generator

A powerful AI-driven application that generates engaging LinkedIn posts with customizable length, language, and topic preferences using few-shot learning and LLMs.

## Features

- **AI-Powered Generation**: Uses LLaMA 3.3 70B via Groq API to generate original LinkedIn posts
- **Customizable Parameters**:
  - **Topic**: Select from predefined categories/tags
  - **Length**: Choose between Short (1-5 lines), Medium (6-10 lines), or Long (11-15 lines)
  - **Language**: Generate in English or Hinglish (mix of Hindi and English)
- **Few-Shot Learning**: Learns from example posts to match writing style
- **Easy-to-Use Interface**: Built with Streamlit for a user-friendly web app

## Project Structure

```
├── main.py                    # Streamlit app entry point
├── post_generator.py          # Core post generation logic
├── llm_helper.py             # LLM configuration and initialization
├── few_shot.py               # Few-shot learning with example posts
├── prepocess.py              # Data preprocessing utilities
├── raw_data.json             # Original training data
├── processed_posts.json      # Processed posts for few-shot examples
├── LICENSE                   # Apache License 2.0
└── README.md                 # This file
```

## Tech Stack

- **Framework**: Streamlit (UI framework)
- **LLM**: LLaMA 3.3 70B via Groq API
- **Language Model Integration**: LangChain
- **Data Processing**: Pandas, JSON

## Installation

### Prerequisites

- Python 3.8 or higher
- Groq API key

### Steps

1. Clone the repository:

   ```bash
   git clone https://github.com/your-username/linkedin-post-generator.git
   cd linkedin-post-generator
   ```

2. Create a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   - Create a `.env` file in the root directory
   - Add your Groq API key:
     ```
     GROQ_API_KEY=your_api_key_here
     ```

## Usage

1. Run the Streamlit app:

   ```bash
   streamlit run main.py
   ```

2. Open your browser and navigate to `http://localhost:8501`

3. Select your preferences:
   - Choose a topic/tag
   - Select post length
   - Choose language (English or Hinglish)

4. Click "Generate" to create your LinkedIn post

## How It Works

1. **Few-Shot Learning**: The `FewShotPosts` class loads processed example posts and filters them based on selected tag, length, and language
2. **Prompt Generation**: Creates a detailed prompt with examples for the LLM
3. **LLM Inference**: Sends the prompt to LLaMA 3.3 70B via Groq API
4. **Output**: Returns a generated LinkedIn post matching your specifications

## Key Files

- **main.py**: Streamlit interface with column-based layout for parameter selection
- **post_generator.py**: `generate_post()` function that orchestrates the generation pipeline
- **few_shot.py**: `FewShotPosts` class that manages example posts and filtering
- **llm_helper.py**: Initializes the Groq LLM with proper configuration

## Data Format

Posts in `processed_posts.json` follow this structure:

```json
[
  {
    "text": "Post content...",
    "tags": ["tag1", "tag2"],
    "language": "English",
    "line_count": 5
  }
]
```

## License

This project is licensed under the Apache License 2.0 - see the LICENSE file for details.

## Future Enhancements

- Database integration for storing generated posts
- Advanced filtering and search options
- Multiple language support
- Post scheduling capabilities
- Analytics dashboard

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues or questions, please open an issue on GitHub.
