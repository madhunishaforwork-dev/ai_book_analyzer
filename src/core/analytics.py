
import textblob
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

class AnalyticsEngine:
    """
    Provides statistical insights, complexity analysis, and sentiment tracking.
    """
    
    def __init__(self, chunks):
        self.chunks = chunks
        self.raw_texts = [d.page_content for d in chunks]
        
    def calculate_reading_complexity(self):
        """Calculates Flesch Reading Ease score via TextBlob/heuristic."""
        # Simple estimation since textblob doesn't have native Flesch
        # Approx: 206.835 - 1.015(words/sentences) - 84.6(syllables/words)
        
        scores = []
        for text in self.raw_texts[:20]: # Sample
            blob = textblob.TextBlob(text)
            sent_count = len(blob.sentences) or 1
            word_count = len(blob.words) or 1
            avg_sent_len = word_count / sent_count
            
            # Rough syllable proxy (vowels)
            syllables = sum(c.lower() in "aeiouy" for c in text)
            avg_syll_per_word = syllables / word_count
            
            score = 206.835 - (1.015 * avg_sent_len) - (84.6 * avg_syll_per_word)
            scores.append(score)
            
        avg_score = np.mean(scores)
        
        # Interpret
        if avg_score > 90: level = "Very Easy (5th Grade)"
        elif avg_score > 60: level = "Standard (8th-9th Grade)"
        elif avg_score > 30: level = "College Level"
        else: level = "Professional / Academic"
        
        return {
            "score": round(avg_score, 1),
            "level": level
        }

    def generate_sentiment_arc(self):
        """Generates sentiment over narrative time (chart)."""
        sentiments = []
        for i, text in enumerate(self.raw_texts):
            blob = textblob.TextBlob(text)
            sentiments.append({
                "Chunk": i + 1,
                "Sentiment": blob.sentiment.polarity
            })
            
        df = pd.DataFrame(sentiments)
        
        # Plotly Chart
        fig = px.line(df, x="Chunk", y="Sentiment", 
                      title="Narrative Tone Arc",
                      color_discrete_sequence=["#3498db"],
                      template="plotly_white")
        fig.update_layout(yaxis_range=[-1, 1], height=300)
        return fig

    def generate_word_distribution(self):
        """Generates a bar chart of top non-stop keywords."""
        all_text = " ".join(self.raw_texts[:50])
        blob = textblob.TextBlob(all_text)
        
        # Stopwords (very basic set for speed, ideally use nltk)
        stopwords = set(['the', 'and', 'a', 'to', 'of', 'in', 'is', 'it', 'that', 'with', 'for', 'as', 'on'])
        words = [w.lower() for w in blob.words if len(w) > 4 and w.lower() not in stopwords]
        
        counts = pd.Series(words).value_counts().head(10)
        df = pd.DataFrame({'Term': counts.index, 'Frequency': counts.values})
        
        fig = px.bar(df, x='Frequency', y='Term', orientation='h',
                     title="Top Key Terms",
                     color_discrete_sequence=["#16a085"],
                     template="plotly_white")
        fig.update_layout(yaxis={'categoryorder':'total ascending'}, height=300)
        return fig
