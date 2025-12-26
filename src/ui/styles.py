
def get_custom_css():
    """Return the custom CSS string for the application"""
    return """
    <style>
    /* Global Styles */
    .main {
        background-color: #fdfbfd;
        color: #2c2c2c;
    }
    
    h1, h2, h3 {
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
        color: #2c2c2c;
    }
    
    /* Headers */
    .main-header {
        font-size: 3rem;
        background: linear-gradient(120deg, #8e44ad 0%, #d2b4de 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: 700;
        letter-spacing: -1px;
    }
    
    /* Card Component */
    .feature-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 4px solid #8e44ad;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(142, 68, 173, 0.1);
        transition: transform 0.2s ease;
    }
    .feature-card:hover {
        transform: translateY(-2px);
    }
    
    /* Analysis Result Card */
    .analysis-card {
        background: white;
        padding: 2rem;
        border-radius: 12px;
        border: 1px solid #e1bee7;
        margin: 1.5rem 0;
        box-shadow: 0 2px 8px rgba(142, 68, 173, 0.05);
    }
    
    /* Chat Interface */
    .chat-user {
        background-color: #9b59b6;
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 15px 15px 2px 15px;
        margin: 0.5rem 0 0.5rem auto;
        max-width: 80%;
        box-shadow: 0 2px 5px rgba(155, 89, 182, 0.2);
    }
    
    .chat-assistant {
        background-color: white;
        color: #2c2c2c;
        padding: 1rem 1.5rem;
        border-radius: 15px 15px 15px 2px;
        margin: 0.5rem auto 0.5rem 0;
        max-width: 80%;
        border-left: 4px solid #8e44ad;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
    }
    
    /* Buttons */
    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
        border: none;
        padding: 0.5rem 1.5rem;
        transition: all 0.2s ease;
    }
    
    .stButton > button:hover {
        box-shadow: 0 4px 12px rgba(142, 68, 173, 0.2);
        color: #8e44ad;
    }
    
    /* Progress Bar */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #8e44ad, #d2b4de);
    }
    </style>
    """
